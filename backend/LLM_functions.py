import os
import pandas as pd
import re
import ollama

class LLMFunctions:
    def __init__(self):
        if not os.path.exists('violationResult.csv'):
            with open('violationResult.csv', 'w') as file:
                file.write('id,impact,tags,description,help,helpUrl,nodeImpact,nodeHtml,nodeTarget,nodeType,message,numViolation\n')
        self.df = pd.read_csv('violationResult.csv')

    def LLM_response(self, system, user, row_index):
        print(f"\n...................................... Call : {row_index}...............................................")

        prompt = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]

        response = ollama.chat(model='codegemma:latest', messages=prompt)
        content = response['message']['content']
    
        return content

    def generate_prompt(self, row_index):
        system_msg = """You are an assistant who will correct web accessibility issues of a provided website.
                I will provide you with an incorrect line of HTML. Provide a correction in the following format:
                
                Correct: [['corrected HTML here']]
                
                Do not add anything else in the response.

                E.g.
                Incorrect: [['<h3></h3>']]
                Correct: [['<h3>Some heading text</h3>']]
                
                Incorrect: [['<img src="image.png">']]
                Correct: [['<img src="image.png" alt="Description">']]
                
                Incorrect: [['<a href=""></a>']]
                Correct: [['<a href="url">Link text</a>']]
                
                Incorrect: [['<div id="accessibilityHome">\n<a aria-label="Accessibility overview" href="https://explore.zoom.us/en/accessibility">Accessibility Overview</a>\n</div>']]
                Correct: [['<div id="accessibilityHome" role="navigation">\n<a aria-label="Accessibility overview" href="https://explore.zoom.us/en/accessibility">Accessibility Overview</a>\n</div>']]
        """

        user_msg = f"""
        Provide a correction for the following. Do not add anything else in the response.

        Incorrect: {self.df['nodeHtml'][row_index]}
        Issue: {self.df['description'][row_index]}
        """
        return system_msg, user_msg

    def get_correction(self, row_index):
        system_msg, user_msg = self.generate_prompt(row_index)
        response = self.LLM_response(system_msg, user_msg, row_index)

        print("LLM Response:", response)

        match = re.search(r"Correct:\s*\[\[(.*?)\]\]", response, re.DOTALL)
        if match:
            corrected_content = match.group(1).strip() 
            corrected_content = corrected_content.replace("'", "").replace('"', "").strip() 
            corrected_content = corrected_content.replace("\n", "").strip()
            return corrected_content
        else:
            # If no corrections are needed, return the original HTML as a fallback
            print("No correction found; returning original HTML.")
            return self.df['nodeHtml'][row_index]



# Instantiate the class and use it
gpt_functions = LLMFunctions()
