import os
import pandas as pd
import re
import ollama

class GemmaFunctions:
    def __init__(self):
        if not os.path.exists('violationsWithFixedContent.csv'):
            with open('violationsWithFixedContent.csv', 'w') as file:
                file.write('id,impact,tags,description,help,helpUrl,nodeImpact,nodeHtml,nodeTarget,nodeType,message,numViolation\n')
        self.df = pd.read_csv('violationsWithFixedContent.csv')

    def LLM_response(self, system, user, row_index):
        print(f"\n...................................... Call : {row_index}...............................................")

        prompt = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]

        response = ollama.chat(model='gemma2:2b', messages=prompt)
        content = response['message']['content']
    
        return content


    def generate_prompt(self, row_index):
        system_msg = """You are an assistant who will correct web accessibility issues of a provided website.
                I will provide you with an incorrect line of HTML. Provide a correction.
                Here are a few examples:

                E.g.
                Incorrect: [['<h3></h3>', '<h3></h3>']]
                Issue: There must be some form of text between heading tags. 
                Correct: [['<h3>Some heading text</h3>', '<h3>Some heading text</h3>']]
                
                Incorrect: [['<img src="image.png">', '<img src="image.png">']]
                Issue: The images lack an alt description. 
                Correct: [['<img src="image.png" alt="Description">', '<img src="image.png" alt="Description">']]
                
                Incorrect: [['<a href=""></a>', '<a href=""></a>']]
                Correct: [['<a href="url">Link text</a>', '<a href="url">Link text</a>']]

                Incorrect: [['<div id="accessibilityHome">\n<a aria-label="Accessibility overview" href="https://explore.zoom.us/en/accessibility">Accessibility Overview</a>\n</div>']]
                Issue: The links are empty and have no URL or text description. 
                Correct: [['<div id="accessibilityHome" role="navigation">\n<a aria-label="Accessibility overview" href="https://explore.zoom.us/en/accessibility">Accessibility Overview</a>\n</div>']]"""

        user_msg = f"""
        Provide a correction for the following. Do not add anything else in the response.

        Incorrect: {self.df['nodeHtml'][row_index]}
        Issue: {self.df['description'][row_index]}
"""
        return system_msg, user_msg

    # Function returns the corrected part of the Gemma response
    def get_correction(self, row_index):
        # Obtain response from Gemma by calling prompt generation and chat functions
        system_msg = self.generate_prompt(row_index)[0]
        user_msg = self.generate_prompt(row_index)[1]
        response = self.LLM_response(system_msg, user_msg,row_index)

        # Extract the "correct" part using regex
        print(response)
        correct_headers = re.search(r"Correct:\s*(\[\[.*\]\])", response)
        if correct_headers:
            return correct_headers.group(1)
        # If no corrections are needed, return the original HTML
        else:
            return self.df['nodeHtml'][row_index]

# Instantiate the class and use it
gpt_functions = GemmaFunctions()
