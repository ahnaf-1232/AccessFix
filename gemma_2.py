import torch
from transformers import pipeline

# print(torch.cuda.is_available())

pipe = pipeline(
    "text-generation",
    model="google/gemma-2-2b-it",
    model_kwargs={"torch_dtype": torch.bfloat16},
    # device="cuda",
)

messages = [
#     {"role":"system", "content":"""You are an assistant who will correct web accessibility issues of a provided website.
#                 I will provide you with an incorrect line of HTML. Provide a correction.
#                 Here are a few examples:

#                 E.g.
#                 Incorrect: [['<h3></h3>', '<h3></h3>']]
#                 Issue: There must be some form of text between heading tags. 
#                 Correct: [['<h3>Some heading text</h3>', '<h3>Some heading text</h3>']]
                
#                 Incorrect: [['<img src="image.png">', '<img src="image.png">']]
#                 Issue: The images lack an alt description. 
#                 Correct: [['<img src="image.png" alt="Description">', '<img src="image.png" alt="Description">']]
                
#                 Incorrect: [['<a href=""></a>', '<a href=""></a>']]
#                 Correct: [['<a href="url">Link text</a>', '<a href="url">Link text</a>']]

#                 Incorrect: [['<div id="accessibilityHome">\n<a aria-label="Accessibility overview" href="https://explore.zoom.us/en/accessibility">Accessibility Overview</a>\n</div>']]
#                 Issue: The links are empty and have no URL or text description. 
#                 Correct: [['<div id="accessibilityHome" role="navigation">\n<a aria-label="Accessibility overview" href="https://explore.zoom.us/en/accessibility">Accessibility Overview</a>\n</div>']]"""
# },
    {"role": "user", "content": """
     You are an assistant who will correct web accessibility issues of a provided website.
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
                Correct: [['<div id="accessibilityHome" role="navigation">\n<a aria-label="Accessibility overview" href="https://explore.zoom.us/en/accessibility">Accessibility Overview</a>\n</div>']]

     
     
        Error: aria-prohibited-attr
        Description: Ensure ARIA attributes are not prohibited for an element's role
        Suggested change: Elements must only use permitted ARIA attributes

        Incorrect: <g fill="rgb(112,117,122)" font-size="9.46345043182373" font-family="Google Sans" font-style="normal" font-weight="500" aria-label="S" transform="matrix(1,0,0,1,12.142000198364258,20.623001098632812)" opacity="1" style="display: block;">
     """},
]

outputs = pipe(messages, max_new_tokens=256)
assistant_response = outputs[0]["generated_text"][-1]["content"].strip()
print(assistant_response)
