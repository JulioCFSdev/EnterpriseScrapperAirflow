import requests
from bs4 import BeautifulSoup
import json
import time
import re

def google_search(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    query = query.replace(' ', '+')
    url = f"https://www.google.com/search?q={query}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None

def get_titles_and_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    titles_links = []
    for item in soup.find_all('div', class_='tF2Cxc'):
        title = item.find('h3')
        link = item.find('a')
        if title and link:
            titles_links.append((title.text, link['href']))
    return titles_links

def get_page_text(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            page_text = ' '.join([para.text for para in paragraphs])
            return page_text
        else:
            return "Falha ao acessar a página"
    except requests.RequestException as e:
        return f"Erro de requisição: {e}"

def main():
    query = "Petrobras"
    html = google_search(query)
    if html:
        titles_links = get_titles_and_links(html)
        results = []
        for i, (title, link) in enumerate(titles_links, 1):
            print(f"{i}. {title}\n{link}")
            page_text = get_page_text(link)
            results.append({
                'title': title,
                'link': link,
                'content': page_text
            })
            time.sleep(2)  # Aguardando para evitar bloqueios pelo Google
        
        # Salvar os resultados em um arquivo JSON
        filename = f"search_google_{query}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        
        print(f"Resultados salvos em {filename}")
    else:
        print("Falha ao realizar a pesquisa no Google")

if __name__ == "__main__":
    main()
