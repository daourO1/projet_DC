import pandas as pd
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

os.environ['WDM_LOG_LEVEL'] = '0' 
os.environ['WDM_LOCAL'] = '1'

options = Options()
options.add_argument("--headless=new") 
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument('--disable-dev-shm-usage')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# URLs à scraper
urls = {
    "vetements-homme": "https://sn.coinafrique.com/categorie/vetements-homme",
    "chaussures-homme": "https://sn.coinafrique.com/categorie/chaussures-homme",
    "vetements-enfants": "https://sn.coinafrique.com/categorie/vetements-enfants",
    "chaussures-enfants": "https://sn.coinafrique.com/categorie/chaussures-enfants",
}

# Liste pour stocker les données
data = []
for categorie, url in urls.items():
    driver.get(url)
    time.sleep(3)
    # Lire le nombre de pages depuis une variable d’environnement
    nb_pages = int(os.environ.get("NB_PAGES", 10))  

    for _ in range(nb_pages):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    annonces = driver.find_elements(By.CLASS_NAME, 'ad__card')
    print(f"{categorie} : {len(annonces)} annonces trouvées")

    for annonce in annonces:
        try:
            type_article = categorie
            prix = annonce.find_element(By.CLASS_NAME, 'ad__card-price').text
            adresse = annonce.find_element(By.CLASS_NAME, 'ad__card-location').text
            adresse = adresse.replace('location_on', '').replace('"', '').replace('é', 'e').replace(',', '/').strip()
            image_lien = annonce.find_element(By.CLASS_NAME, 'ad__card-img').get_attribute('src')

            data.append([type_article, prix, adresse, image_lien])
        except:
            continue
driver.quit()

# Nettoyage des données
df = pd.DataFrame(data, columns=["Type", "Prix", "Adresse", "Image_lien"])
df = df.drop_duplicates().dropna()

# Sauvegarde CSV
df.to_csv("donnees/coinafrique_nettoye.csv", index=False)



