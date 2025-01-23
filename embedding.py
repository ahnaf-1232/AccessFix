from sentence_transformers import SentenceTransformer, util

# Load models
model1 = SentenceTransformer('all-MiniLM-L6-v2')
model2 = SentenceTransformer('mxbai-embed-large')  # Hypothetical, adjust according to actual availability

# Example text
texts = ["Accessibility guidelines are essential for web development.", 
         "Semantic analysis boosts the effectiveness of search engines."]

# Generate embeddings
embeddings1 = model1.encode(texts)
embeddings2 = model2.encode(texts)

# Compare embeddings
similarity1 = util.pytorch_cos_sim(embeddings1[0], embeddings1[1])
similarity2 = util.pytorch_cos_sim(embeddings2[0], embeddings2[1])

print("Similarity by model 1:", similarity1)
print("Similarity by model 2:", similarity2)
