import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_file(url, folder):
    local_filename = os.path.join(folder, os.path.basename(urlparse(url).path))
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        return local_filename
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

def download_website(url, output_folder):
    create_directory(output_folder)
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch the website")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Download and rewrite links for CSS, JS, and Images
    assets_folder = os.path.join(output_folder, "assets")
    create_directory(assets_folder)
    
    for tag in soup.find_all(["link", "script", "img"]):
        if tag.name == "link" and tag.get("rel") == ["stylesheet"]:
            file_url = urljoin(url, tag["href"])
            local_file = download_file(file_url, assets_folder)
            if local_file:
                tag["href"] = os.path.relpath(local_file, output_folder)
        elif tag.name == "script" and tag.get("src"):
            file_url = urljoin(url, tag["src"])
            local_file = download_file(file_url, assets_folder)
            if local_file:
                tag["src"] = os.path.relpath(local_file, output_folder)
        elif tag.name == "img" and tag.get("src"):
            file_url = urljoin(url, tag["src"])
            local_file = download_file(file_url, assets_folder)
            if local_file:
                tag["src"] = os.path.relpath(local_file, output_folder)
    
    # Save index.html
    with open(os.path.join(output_folder, "index.html"), "w", encoding="utf-8") as f:
        f.write(str(soup))
    
    print("Website cloned successfully!")

if __name__ == "__main__":
    website_url = input("Enter the React website URL: ")
    output_directory = "cloned_react_website"
    download_website(website_url, output_directory)
