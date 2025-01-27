import os
import chromadb.errors
import pandas as pd
import re
import ollama
import chromadb
import json
import openai
from bs4 import BeautifulSoup
from typing import Optional, Match


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

    def LLM_response(self, system, user):
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
        # print(f"Incorrect: {self.df['nodeHtml'][row_index]}")
        print(f"Response: {response.choices[0].message.content}")
        return response.choices[0].message.content
    
        # response = ollama.chat(model='codegemma:latest', messages=prompt)
        # content = response['message']['content']
        
        # return content

    def generate_prompt(self, row_index, guideline):
        system_msg = """You are an assistant who will correct web accessibility issues of a provided website.
                I will provide you with an incorrect line of HTML and some guidelines for that. Provide a correction in [['response']] format without any extra. Do not respond in any other format.
                Here are a few examples:

                E.g.
                Incorrect: [['<h3></h3>']]
                Issue: There must be some form of text between heading tags. 
                Guideline: WCAG 2.4.6: Headings and Labels - Provide headings and labels that describe topic or purpose.
                Correct: [['<h3>Some heading text</h3>']]

                Incorrect: [['<img src="image.png">']]
                Issue: The images lack an alt description. 
                Guideline: WCAG 1.1.1: Non-text Content - All non-text content that is presented to the user has a text alternative that serves the equivalent purpose.
                Correct: [['<img src="image.png" alt="Description">']]

                Incorrect: [['<div id="accessibilityHome">\n<a aria-label="Accessibility overview" href="https://explore.zoom.us/en/accessibility">Accessibility Overview</a>\n</div>']]
                Issue: The links have an unclear purpose based on the link text alone.
                Guideline: WCAG 2.4.4: Link Purpose (In Context) - The purpose of each link can be determined from the link text alone or from the link text together with its programmatically determined link context.
                Correct: [['<div id="accessibilityHome" role="navigation">\n<a aria-label="Accessibility overview" href="https://explore.zoom.us/en/accessibility">Accessibility Overview</a>\n</div>']]
        """

        user_msg = f"""
        Provide a correction for the following. Do not add anything else in the response.
        Error: {self.df['id'][row_index]}
        Incorrect: {self.df['nodeHtml'][row_index]}
        Issue: {self.df['description'][row_index]}
        Guideline: {guideline}
        Suggested change: {self.df['help'][row_index]}
        """
        return system_msg, user_msg

    # def get_relevant_data(self, issue_description):
    #     response = ollama.embeddings(
    #         prompt=issue_description,
    #         model="mxbai-embed-large"
    #     )

    #     results = self.collection.query(
    #         query_embeddings=[response["embedding"]],
    #         n_results=3
    #     )
    #     data = "\n\n".join(results['documents'][0])
    #     return data

    def get_correction(self, row_index: int):
        query_prompt = f"What are the guidelines related to {self.df['description'][row_index]} in accessibility?"

        response = ollama.embeddings(
            prompt=query_prompt, 
            model="mxbai-embed-large"
        )
        results = self.collection.query(
            query_embeddings=[response["embedding"]], n_results=3
        )
        retrieved_data = results["documents"][0][0]  # Assume correct retrieval for simplicity

        system_msg, user_msg = self.generate_prompt(row_index, retrieved_data)
        response = self.LLM_response(system_msg, user_msg)

        # Adjusted regex pattern to handle single quotes and correct formatting without "Correct:" prefix
        correct_headers: Optional[Match[str]] = re.search(r"\[\['(.*?)'\]\]", response)

        if correct_headers:
            print("Correction found:", correct_headers.group(1))
            return correct_headers.group(1)
        else:
            print("No correction found; returning original HTML.")
            return self.df['nodeHtml'][row_index]


gpt_functions = LLMFunctions()