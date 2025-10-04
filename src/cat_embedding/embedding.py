import torch
import clip
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

def get_embedding(image_path):
    image = preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0).to(device)
    with torch.no_grad():
        emb = model.encode_image(image)
    return emb.cpu().numpy()

def compare_images(img1, img2, threshold=0.8):
    emb1 = get_embedding(img1)
    emb2 = get_embedding(img2)
    sim = cosine_similarity(emb1, emb2)[0][0]
    return sim, sim > threshold

