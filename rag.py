import ollama
import chromadb
import json

with open('wcag.json', 'r', encoding='utf-8') as f:
    wcag_data = json.load(f)

client = chromadb.Client()
collection = client.create_collection(name="wcag_docs")

for item in wcag_data:
    for guideline in item['guidelines']:
        for criterion in guideline.get('success_criteria', []):
            title1 = item['title']
            ref_id1 = item['ref_id']

            title2 = guideline['title']
            ref_id2 = guideline['ref_id']

            ref_id = criterion['ref_id']
            title = criterion['title']
            description = criterion['description']
            url = criterion['url']
            level = criterion.get('level', 'N/A')
            
            doc = (
                f"Top-level Title: {title1}\n"
                f"Top-level ID: {ref_id1}\n\n"
                f"Guideline Title: {title2}\n"
                f"Guideline ID: {ref_id2}\n\n"
                f"Success Criterion ID: {ref_id}\n"
                f"Success Criterion Title: {title}\n"
                f"Description: {description}\n"
                f"URL: {url}\n"
                f"Level: {level}\n"
            )
            
            response = ollama.embeddings(model="mxbai-embed-large", prompt=doc)
            embedding = response["embedding"]
            
            collection.add(
                ids=[ref_id],
                embeddings=[embedding],
                documents=[doc]
            )



print("Data chunks created and added to the collection successfully!")


prompt = """What are the guidelines for Focus Appearance in accessibility? 

Asnwer in the following format: 
Success Criterion ID: {ref_id}
Success Criterion Title: {title}
Description: {description}
URL: {url}
Level: {level}
"""

response = ollama.embeddings(
    prompt=prompt,
    model="mxbai-embed-large"
)

results = collection.query(
    query_embeddings=[response["embedding"]],
    n_results=3
)
data = results['documents'][0][0]

output = ollama.generate(
    model="codegemma:latest",
    prompt=f"Using this data: {data}. Respond to this prompt: {prompt}"
)

print(output['response'])
