import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

# URLs à scraper
urls = {
    "vetements-homme": "https://sn.coinafrique.com/categorie/vetements-homme",
    "chaussures-homme": "https://sn.coinafrique.com/categorie/chaussures-homme",
    "vetements-enfants": "https://sn.coinafrique.com/categorie/vetements-enfants",
    "chaussures-enfants": "https://sn.coinafrique.com/categorie/chaussures-enfants",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

data = []

for categorie, url in urls.items():
    print(f"Scraping {categorie} ...")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Erreur {response.status_code} sur {url}")
        continue

    soup = BeautifulSoup(response.text, 'html.parser')

    # Trouver toutes les annonces (adapté à ta page)
    annonces = soup.find_all(class_='ad__card')
    print(f"{categorie} : {len(annonces)} annonces trouvées")

    for annonce in annonces:
        try:
            prix_tag = annonce.find(class_='ad__card-price')
            prix = prix_tag.get_text(strip=True) if prix_tag else ""

            adresse_tag = annonce.find(class_='ad__card-location')
            adresse = adresse_tag.get_text(strip=True) if adresse_tag else ""
            adresse = adresse.replace('location_on', '').replace('"', '').replace('é', 'e').replace(',', '/').strip()

            img_tag = annonce.find(class_='ad__card-img')
            image_lien = img_tag['src'] if img_tag and 'src' in img_tag.attrs else ""

            data.append([categorie, prix, adresse, image_lien])
        except Exception as e:
            # print(f"Erreur sur une annonce: {e}")
            continue

    # Pour éviter d'envoyer trop de requêtes trop vite
    time.sleep(2)

# Nettoyage des données
df = pd.DataFrame(data, columns=["Type", "Prix", "Adresse", "Image_lien"])
df = df.drop_duplicates().dropna()

# Création dossier donnees si inexistant
os.makedirs("donnees", exist_ok=True)

# Sauvegarde CSV
df.to_csv("donnees/coinafrique_nettoye.csv", index=False)
print("Scraping terminé, données sauvegardées dans donnees/coinafrique_nettoye.csv")
