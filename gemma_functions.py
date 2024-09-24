import os
import torch
from transformers import pipeline
import pandas as pd
import re

class GemmaFunctions:
    def __init__(self):
        # Check if the CSV exists; if not, create it
        if not os.path.exists('violationsWithFixedContent.csv'):
            with open('violationsWithFixedContent.csv', 'w') as file:
                file.write('id,impact,tags,description,help,helpUrl,nodeImpact,nodeHtml,nodeTarget,nodeType,message,numViolation\n')
        self.df = pd.read_csv('violationsWithFixedContent.csv')

        # Initialize the Gemma pipeline
        self.pipe = pipeline(
            "text-generation",
            model="google/gemma-2-2b-it",
            model_kwargs={"torch_dtype": torch.bfloat16},
            # device="cuda"  # Uncomment if running on GPU
        )

    # Function to get responses from the Gemma model given system and user messages
    def GPT_response(self, system, user):
        # Combine system and user messages into a single prompt for Gemma
        print("\n...................................... new call ...............................................")
      
        prompt = f"{system}\n\n{user}"
        # Use the pipeline to generate text based on the prompt
        outputs = self.pipe(prompt, max_new_tokens=128)
        # Extract the generated text
        # response = outputs[0]["generated_text"][-1]["content"].strip()
        response = outputs[0]["generated_text"].strip()
        return response

    """BASELINE ReAct Prompt"""

    # Function returns system message and user message for a given row index of the dataframe
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
        Error: {self.df['id'][row_index]}
        Description: {self.df['description'][row_index]}
        Suggested change: {self.df['help'][row_index]}

        Incorrect: {self.df['nodeHtml'][row_index]}"""
        return system_msg, user_msg

    """Function for getting GPT corrections"""

    # Function returns the corrected part of the Gemma response
    def get_correction(self, row_index):
        # Obtain response from Gemma by calling prompt generation and chat functions
        system_msg = self.generate_prompt(row_index)[0]
        user_msg = self.generate_prompt(row_index)[1]
        response = self.GPT_response(system_msg, user_msg)

        # Extract the "correct" part using regex
        correct_headers = re.search(r"Correct:\s*(\[\[.*\]\])", response)
        if correct_headers:
            return correct_headers.group(1)
        # If no corrections are needed, return the original HTML
        else:
            return self.df['nodeHtml'][row_index]

# Instantiate the class and use it
gpt_functions = GemmaFunctions()
