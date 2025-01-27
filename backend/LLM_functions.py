import os
import chromadb.errors
import pandas as pd
import re
import ollama
import chromadb
import json
import openai
from bs4 import BeautifulSoup


class LLMFunctions:
    def __init__(self):
        if not os.path.exists('violationResult.csv'):
            with open('violationResult.csv', 'w') as file:
                file.write('id,impact,tags,description,help,helpUrl,nodeImpact,nodeHtml,nodeTarget,nodeType,numViolation\n')
        self.df = pd.read_csv('violationResult.csv')
        self.client = chromadb.Client()
        self.collection = self.get_or_create_collection("wcag_docs")
        with open('wcag.json', 'r', encoding='utf-8') as f:
            self.wcag_data = json.load(f)
        self.populate_collection()

    def get_or_create_collection(self, name):
        try:
            return self.client.get_collection(name=name)
        except chromadb.errors.InvalidCollectionException:
            return self.client.create_collection(name=name)

    def populate_collection(self):
        existing_ids = set(self.collection.get()['ids'])  # Get existing IDs
        
        for item in self.wcag_data:
            for guideline in item['guidelines']:
                for criterion in guideline.get('success_criteria', []):
                    ref_id = criterion['ref_id']
                    
                    # Skip if ID already exists
                    if ref_id in existing_ids:
                        continue
                    
                    existing_ids.add(ref_id)
                    
                    doc = f"WCAG: {ref_id} : {criterion['title']} - {criterion['description']}\n"
                    
                    response = ollama.embeddings(model="mxbai-embed-large", prompt=doc)
                    embedding = response["embedding"]
                    
                    self.collection.add(
                        ids=[ref_id],
                        embeddings=[embedding],
                        documents=[doc]
                    )

    def LLM_response(self, system, user, row_index):
        # print(f"\n...................................... Call : {row_index}...............................................")

        prompt = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        
        return response.choices[0].message.content
    
        # response = ollama.chat(model='codegemma:latest', messages=prompt)
        # content = response['message']['content']
        
        # return content

    def generate_prompt(self, row_index):
        system_msg = """You are an assistant who will correct web accessibility issues of a provided website.
                I will provide you with an incorrect line of HTML and relevant information from a knowledge base. Provide a correction in the following format:

                Correct: [['corrected HTML here']]

                Do not add anything else in the response.
        """

        user_msg = f"""
        Provide a correction for the following. Do not add anything else in the response.

        Incorrect: {self.df['nodeHtml'][row_index]}
        Issue: {self.df['description'][row_index]}

        Relevant information from the knowledge base:
        {self.get_relevant_data(self.df['description'][row_index])}
        """
        return system_msg, user_msg

    def get_relevant_data(self, issue_description):
        response = ollama.embeddings(
            prompt=issue_description,
            model="mxbai-embed-large"
        )

        results = self.collection.query(
            query_embeddings=[response["embedding"]],
            n_results=3
        )
        data = "\n\n".join(results['documents'][0])
        return data

    def get_correction(self, row_index):
        system_msg, user_msg = self.generate_prompt(row_index)
        response = self.LLM_response(system_msg, user_msg, row_index)

        # Extract correction
        match = re.search(r"Correct:\s*\[\[(.*?)\]\]", response, re.DOTALL)
        if match:
            print("Correction found: ", match.group(1))
            corrected_content = match.group(1).strip()
            # Remove new lines and unnecessary spaces around '=' and inside tags
            corrected_content = re.sub(r'\s*\n\s*', ' ', corrected_content)  # replace new lines with a single space
            corrected_content = re.sub(r'\s*=\s*', '=', corrected_content)  # remove spaces around '='
            corrected_content = re.sub(r'\s+', ' ', corrected_content)  # collapse multiple spaces into one
            print("Corrected content: ", corrected_content)
            return corrected_content
     
            
        else:
            print("No correction found; returning original HTML.")
            corrected_content = self.df['nodeHtml'][row_index]

        return corrected_content


gpt_functions = LLMFunctions()