import requests
from bs4 import BeautifulSoup

def get_page_text(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text(separator=' ', strip=True)
            return page_text
        else:
            return f"Failed to retrieve the page. Status code: {response.status_code}"
    
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"
