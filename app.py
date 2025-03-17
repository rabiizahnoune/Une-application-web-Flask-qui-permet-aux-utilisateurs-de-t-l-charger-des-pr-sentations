from flask import Flask, request, jsonify, send_file
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
import time
import os
import img2pdf
import shutil

app = Flask(__name__, static_folder='static')

OUTPUT_DIR = "downloaded_images"
PDF_OUTPUT = "output.pdf"

# Configurer Google Custom Search API
API_KEY = "AIzaSyCzQXLdULy3XnNHhEYRb_Byb3GKugCXA0g"  # Votre clé actuelle (à vérifier)
CX = "c0330892ee6024845"  # Votre CX actuel


def google_search(query):
    try:
        service = build("customsearch", "v1", developerKey=API_KEY)
        res = service.cse().list(q=query, cx=CX, num=1, siteSearch="slideshare.net").execute()
        if "items" in res and res["items"]:
            return res["items"][0]["link"]
        return None
    except HttpError as e:
        return f"Erreur API Google: {str(e)}"
    except Exception as e:
        return f"Erreur inattendue dans la recherche: {str(e)}"

def download_slides(url):
    print(f"Tentative de chargement de l'URL : {url}")
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(300)

    try:
        driver.get(url)
        time.sleep(5)
        for slide_num in range(0, 16):
            try:
                slide = driver.find_element(By.ID, f"slide-image-{slide_num}")
                srcset = slide.get_attribute("srcset")
                if srcset:
                    high_res_url = [url.split(" ")[0] for url in srcset.split(", ") if "2048w" in url][0]
                    response = requests.get(high_res_url, stream=True, timeout=30)
                    response.raise_for_status()
                    file_path = os.path.join(OUTPUT_DIR, f"slide_{slide_num}.jpg")
                    with open(file_path, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            file.write(chunk)
                    print(f"Image téléchargée : slide_{slide_num}.jpg")
                else:
                    print(f"Pas de srcset pour slide-image-{slide_num}")
            except Exception as e:
                print(f"Erreur avec slide-image-{slide_num}: {str(e)}")
    except Exception as e:
        print(f"Erreur lors du chargement de la page : {str(e)}")
        return False
    finally:
        driver.quit()
    return True

def merge_to_pdf():
    images = [os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR) if f.endswith(".jpg")]
    images.sort()
    with open(PDF_OUTPUT, "wb") as f:
        f.write(img2pdf.convert(images))
    return PDF_OUTPUT

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    tech = data.get("technology", "").strip()
    if not tech:
        return jsonify({"success": False, "message": "Please enter a technology name"})

    query = f"{tech} presentation slideshare site:slideshare.net"
    slideshare_url = google_search(query)
    
    if isinstance(slideshare_url, str) and "Erreur" in slideshare_url:
        return jsonify({"success": False, "message": slideshare_url})
    if not slideshare_url:
        return jsonify({"success": False, "message": "No SlideShare presentation found"})

    if not download_slides(slideshare_url):
        return jsonify({"success": False, "message": "Failed to load SlideShare page"})

    if not os.listdir(OUTPUT_DIR):
        return jsonify({"success": False, "message": "No slides found to download"})

    pdf_path = merge_to_pdf()
    return jsonify({"success": True, "message": "Download complete!", "pdf_path": f"/download_pdf/{os.path.basename(pdf_path)}"})

@app.route('/download_pdf/<filename>')
def download_pdf(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
