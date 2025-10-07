# src/cat_embedding/__main__.py
import argparse, json, os
from pathlib import Path
from .schema import CatMeta
from .gallery import build_gallery, load_gallery, build_vector, match_query

def main():
    ap = argparse.ArgumentParser("cat-embedding (Re-ID)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="메타데이터로 갤러리 벡터 DB 생성")
    b.add_argument("--meta", required=True, help="metadata.json or .jsonl")
    b.add_argument("--out",  required=True, help="output npz path")
    b.add_argument("--bounds", default=None, help="lat/lon bounds json: [min_lat,max_lat,min_lon,max_lon]")

    m = sub.add_parser("match", help="쿼리 메타데이터 1건(or 여러건) 매칭")
    m.add_argument("--gallery", required=True)
    m.add_argument("--query",   required=True, help="query metadata json (one or list)")
    m.add_argument("--bounds",  default=None)
    m.add_argument("--thr",     type=float, default=0.80)
    m.add_argument("--margin",  type=float, default=0.05)

    c = sub.add_parser("clean", help="임베딩 정보 및 갤러리 파일 삭제")
    c.add_argument("--gallery", help="삭제할 갤러리 파일 (.npz)")
    c.add_argument("--all", action="store_true", help="모든 임베딩 관련 파일 삭제")
    c.add_argument("--force", action="store_true", help="확인 없이 강제 삭제")

    args = ap.parse_args()

    if args.cmd == "build":
        bounds = json.loads(args.bounds) if args.bounds else None
        
        # 메타데이터 파일 확인
        if not os.path.exists(args.meta):
            print(f"❌ 메타데이터 파일을 찾을 수 없습니다: {args.meta}")
            print("💡 메타데이터 파일을 생성하세요:")
            print("   cat > metadata.json << 'EOF'")
            print("[")
            print("  {")
            print("    \"cat_id\": \"cat_001\",")
            print("    \"image_path\": \"cat1.jpg\",")
            print("    \"timestamp\": \"2024-10-04T10:00:00\",")
            print("    \"lat\": 37.5665,")
            print("    \"lon\": 126.9780,")
            print("    \"ear_tip\": \"left\",")
            print("    \"nose_color\": \"pink\",")
            print("    \"eye_color\": \"yellow\",")
            print("    \"coat_type\": \"ginger_tabby\",")
            print("    \"has_stripes\": true")
            print("  }")
            print("]")
            print("EOF")
            return
        
        build_gallery(args.meta, args.out, bounds=bounds)
        print(f"✅ gallery saved to {args.out}")

    elif args.cmd == "match":
        bounds = json.loads(args.bounds) if args.bounds else None
        
        # 갤러리 파일 확인
        if not os.path.exists(args.gallery):
            print(f"❌ 갤러리 파일을 찾을 수 없습니다: {args.gallery}")
            print("💡 먼저 갤러리를 구축하세요:")
            print(f"   cat-embedding build --meta metadata.json --out {args.gallery}")
            return
        
        # 쿼리 파일 확인
        if not os.path.exists(args.query):
            print(f"❌ 쿼리 파일을 찾을 수 없습니다: {args.query}")
            print("💡 쿼리 파일을 생성하세요:")
            print("   cat > query.json << 'EOF'")
            print("{")
            print("  \"cat_id\": \"query_cat\",")
            print("  \"image_path\": \"cat1.jpg\",")
            print("  \"timestamp\": \"2024-10-04T12:00:00\",")
            print("  \"lat\": 37.5665,")
            print("  \"lon\": 126.9780,")
            print("  \"ear_tip\": \"left\",")
            print("  \"nose_color\": \"pink\",")
            print("  \"eye_color\": \"yellow\",")
            print("  \"coat_type\": \"ginger_tabby\",")
            print("  \"has_stripes\": true")
            print("}")
            print("EOF")
            return
        
        gal = load_gallery(args.gallery)
        payload = json.loads(open(args.query, "r", encoding="utf-8").read())
        metas = [CatMeta(**payload)] if isinstance(payload, dict) else [CatMeta(**x) for x in payload]
        # multi-shot: 쿼리 여러 장이면 평균 벡터로
        vecs = [build_vector(m, bounds=bounds) for m in metas]
        import numpy as np
        q = np.mean(vecs, axis=0)  # 간단 평균 (필요 시 상위 p% 평균 등으로 개선)
        pred, sim = match_query(q, gal, threshold=args.thr, margin=args.margin)
        
        # 결과 출력
        result = {"pred": pred, "sim": round(float(sim),4)}
        print(json.dumps(result, ensure_ascii=False))
        
        # 새로운 개체로 확인된 경우 metadata 추가 제안
        # (실제 사용: UNKNOWN이고 임계값 미만인 경우)
        # (테스트용: 강제로 새로운 개체로 간주하려면 아래 주석 해제)
        is_new_entity = (pred == "UNKNOWN" and sim < args.thr)
        # is_new_entity = True  # 테스트용: 항상 새로운 개체로 간주
        if is_new_entity:
            print(f"\n🆕 새로운 개체로 확인되었습니다! (유사도: {sim:.4f})")
            print("이 개체를 갤러리에 추가하시겠습니까?")
            
            # 메타데이터 파일 경로 추정
            metadata_file = "metadata.json"
            if os.path.exists(metadata_file):
                # 기존 메타데이터에 추가
                try:
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        existing_data = json.load(f)
                    
                    # 새로운 개체 ID 생성
                    existing_ids = [item.get("cat_id", "") for item in existing_data if isinstance(item, dict)]
                    new_id = f"cat_{len(existing_ids) + 1:03d}"
                    
                    # 쿼리 메타데이터를 새로운 ID로 업데이트
                    new_meta = metas[0].model_dump()
                    new_meta["cat_id"] = new_id
                    # datetime 객체를 문자열로 변환
                    if "timestamp" in new_meta and hasattr(new_meta["timestamp"], "isoformat"):
                        new_meta["timestamp"] = new_meta["timestamp"].isoformat()
                    
                    # 기존 데이터에 추가
                    existing_data.append(new_meta)
                    
                    # 사용자 확인
                    print(f"📝 추가할 개체 정보:")
                    print(f"   - ID: {new_id}")
                    print(f"   - 이미지: {new_meta['image_path']}")
                    print(f"   - 위치: ({new_meta.get('lat', 'N/A')}, {new_meta.get('lon', 'N/A')})")
                    
                    confirm = input(f"\n{metadata_file}에 추가하고 갤러리를 재구축하시겠습니까? (y/N): ").strip().lower()
                    
                    if confirm in ['y', 'yes']:
                        # 메타데이터 파일 업데이트
                        with open(metadata_file, "w", encoding="utf-8") as f:
                            json.dump(existing_data, f, indent=2, ensure_ascii=False)
                        print(f"✅ {metadata_file}에 {new_id} 추가됨")
                        
                        # 갤러리 재구축
                        print("🔄 갤러리 재구축 중...")
                        build_gallery(metadata_file, args.gallery, bounds=bounds)
                        print(f"✅ 갤러리 재구축 완료: {args.gallery}")
                        print(f"💡 이제 {new_id}로 매칭할 수 있습니다!")
                    else:
                        print("❌ 추가가 취소되었습니다")
                        
                except Exception as e:
                    print(f"❌ 메타데이터 업데이트 중 오류: {e}")
            else:
                print(f"❌ 메타데이터 파일을 찾을 수 없습니다: {metadata_file}")
                print("💡 먼저 메타데이터 파일을 생성하세요")

    elif args.cmd == "clean":
        clean_embedding_files(args)

def clean_embedding_files(args):
    """임베딩 관련 파일들을 삭제하는 함수"""
    deleted_files = []
    
    if args.all:
        # 모든 임베딩 관련 파일 패턴
        patterns = ["*.npz", "*_gallery*.npz", "*_embedding*.npz", "gallery*.npz"]
        current_dir = Path(".")
        
        for pattern in patterns:
            for file_path in current_dir.glob(pattern):
                if file_path.is_file():
                    deleted_files.append(str(file_path))
                    file_path.unlink()
        
        # 메타데이터 파일도 삭제 (선택사항)
        metadata_files = ["test_metadata.json", "query.json", "metadata.json"]
        for file_name in metadata_files:
            file_path = Path(file_name)
            if file_path.exists():
                deleted_files.append(str(file_path))
                file_path.unlink()
    
    elif args.gallery:
        # 특정 갤러리 파일만 삭제
        gallery_path = Path(args.gallery)
        if gallery_path.exists():
            deleted_files.append(str(gallery_path))
            gallery_path.unlink()
        else:
            print(f"❌ 파일을 찾을 수 없습니다: {args.gallery}")
            return
    
    else:
        print("❌ --gallery 또는 --all 옵션을 지정해주세요")
        return
    
    # 확인 메시지 (--force가 아닌 경우)
    if not args.force and deleted_files:
        print("🗑️  삭제할 파일들:")
        for file in deleted_files:
            print(f"   - {file}")
        
        confirm = input("\n정말 삭제하시겠습니까? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ 삭제가 취소되었습니다")
            return
    
    # 파일 삭제 실행
    if deleted_files:
        print(f"✅ {len(deleted_files)}개 파일이 삭제되었습니다:")
        for file in deleted_files:
            print(f"   - {file}")
    else:
        print("ℹ️  삭제할 임베딩 파일이 없습니다")

if __name__ == "__main__":
    main()
