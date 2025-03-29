import os
import requests
import shutil
import zipfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def ensure_folder_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def download_file(url, folder):
    ensure_folder_exists(folder)
    filename = os.path.basename(urlparse(url).path) or "index.html"
    local_path = os.path.join(folder, filename)
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return filename
    except requests.RequestException:
        return None

def clone_website(url, output_folder):
    ensure_folder_exists(output_folder)
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    assets = {'img': 'src', 'link': 'href', 'script': 'src'}
    
    for tag, attr in assets.items():
        for element in soup.find_all(tag):
            src = element.get(attr)
            if src and not src.startswith(('http', 'https')):
                src = urljoin(url, src)
            
            filename = download_file(src, output_folder)
            if filename:
                element[attr] = filename
    
    index_path = os.path.join(output_folder, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    return output_folder

def create_zip(folder):
    zip_filename = folder + '.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder))
    return zip_filename

if __name__ == "__main__":
    website_url = "https://unige.it/"
    output_folder = "cloned_websites"
    
    print("Cloning website...")
    cloned_folder = clone_website(website_url, output_folder)
    
    print("Creating ZIP file...")
    zip_path = create_zip(cloned_folder)
    
    print(f"Website cloned successfully! ZIP file created: {zip_path}")
