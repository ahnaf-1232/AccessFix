import requests
from bs4 import BeautifulSoup
import os

def fetch_and_save_data(url, path):
    # Make a GET request to the URL   
    print("fetching the code............")
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Save the HTML content to a file
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f"HTML content has been saved to {path}")
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
