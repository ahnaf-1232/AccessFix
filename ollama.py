import pandas as pd
import ollama

# Load the CSV file with diverse violations
file_path = "D:\Code\SPL3\diverse_accessibility_violations.csv"
df = pd.read_csv(file_path)

# Define a function to interact with Ollama for correcting HTML code
def correct_html_violation(violated_code):
    user_input = f"Incorrect: {violated_code}"
    system_input = f"""
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

        Now provide a correction for the following. Do not add anything else in the response.
        {user_input}
    """
    try:
        # Use Ollama to get a response
        response = ollama.chat(model='llama3.2:latest', messages=[
            {'role': 'user', 'content': system_input},
        ])
        print(response['message']['content'])
        return response['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

# Apply the correction function to each row in the dataset
df['corrected_code'] = df['code_with_violation'].apply(lambda x: correct_html_violation(x))

# Save the updated DataFrame to a new CSV file
updated_file_path = "D:\Code\SPL3\diverse_accessibility_violations.csv"
df.to_csv(updated_file_path, index=False)

updated_file_path
