# src/cat_embedding/__main__.py
import argparse, json
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

    args = ap.parse_args()

    bounds = json.loads(args.bounds) if args.bounds else None

    if args.cmd == "build":
        build_gallery(args.meta, args.out, bounds=bounds)
        print(f"✅ gallery saved to {args.out}")

    elif args.cmd == "match":
        gal = load_gallery(args.gallery)
        payload = json.loads(open(args.query, "r", encoding="utf-8").read())
        metas = [CatMeta(**payload)] if isinstance(payload, dict) else [CatMeta(**x) for x in payload]
        # multi-shot: 쿼리 여러 장이면 평균 벡터로
        vecs = [build_vector(m, bounds=bounds) for m in metas]
        import numpy as np
        q = np.mean(vecs, axis=0)  # 간단 평균 (필요 시 상위 p% 평균 등으로 개선)
        pred, sim = match_query(q, gal, threshold=args.thr, margin=args.margin)
        print(json.dumps({"pred": pred, "sim": round(float(sim),4)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
