

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import subprocess


# CONFIGURATION 
st.set_page_config(page_title="CoinAfrique Scraper App", layout="wide")

# Les dossiers
RAW_CSV = "donnees/webscraper_bruts.csv"
CLEAN_CSV = "donnees/webscraper_nettoyes.csv"
SCRAPED_CSV = "projet_DC/coinafrique_nettoye.csv"

# Menu principal
st.sidebar.title("📂 Navigation")
menu = st.sidebar.radio("Aller à :", [
    "🏠 Accueil",
    "🕸️ Scraper CoinAfrique (BeautifulSoup)",
    "📥 Données Web Scraper (brutes)",
    "📊 Dashboard des données nettoyées",
    "📝 Formulaire kobo"
])


# Acceuil 
if menu == "🏠 Accueil":
    st.title(" Application de Scraping CoinAfrique")
    st.markdown("""
    Bienvenue ! Cette app vous permet de :
    - Scraper les annonces CoinAfrique (vetements-homme, chaussures-homme, vetements-enfants et chaussures-enfants )
    - Télécharger les données brutes issues de Web Scraper
    - Voir des statistiques nettoyées des données issues du web scraper
    - Remplir un formulaire kobotoolbox
    """)


# BeautifulSoup
elif menu == "🕸️ Scraper CoinAfrique (BeautifulSoup)":
    st.title("🚀 Lancer le scraping avec BeautifulSoup")
    nb_pages = st.number_input("📄 Nombre de pages à scraper :", min_value=1, max_value=10, value=1)
    st.info("Cliquez sur le bouton pour lancer le scraping en fonction du nombre de pages choisi.")
    if st.button("Lancer le scraping"):
        try:
            env = os.environ.copy()
            env["NB_PAGES"] = str(nb_pages)
            result = subprocess.run(
                ["python", "codes/Donnee_Nettoyer.py"],
                env=env,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                st.success(f"✅ Scraping terminé avec {nb_pages} pages.")
                try:
                    df = pd.read_csv("donnees/coinafrique_nettoye.csv") 
                    st.write(f"Nombre de lignes : {len(df)}")
                    st.dataframe(df)
                    st.download_button("📥 Télécharger ces données", df.to_csv(index=False), "coinafrique_nettoye_bs4.csv")
                except Exception as e:
                    st.error(f"Erreur lors de l'affichage des données : {e}")
            else:
                st.error("❌ Une erreur est survenue pendant le scraping.")
                st.text(result.stderr)
        except Exception as e:
            st.error(f"Erreur : {e}")




# Données Web Scraper brutes
elif menu == "📥 Données Web Scraper (brutes)":
    st.title("📥 Données brutes (Web Scraper)")

    try:
        df = pd.read_csv(RAW_CSV)
        lignes_total = len(df)
        lignes_par_page = 84  

        # L'utilisateur choisit combien de pages il veut voir
        max_pages = lignes_total // lignes_par_page
        nb_pages = st.number_input(
            "📄 Nombre de pages à afficher :",
            min_value=1,
            max_value=max_pages if max_pages > 0 else 1,
            value=1
        )
        # Calcule du nombre de ligne à afficher
        nb_lignes = nb_pages * lignes_par_page
        st.write(f"Affichage des {nb_lignes} premières lignes (≈ {nb_pages} pages)")
        st.dataframe(df.head(nb_lignes))
        st.download_button("📤 Télécharger CSV brut", df.to_csv(index=False), "webscraper_bruts.csv")
    
    except Exception as e:
        st.error("❌ Impossible de lire le fichier brut.")
        st.error(f"Erreur : {e}")


# Dashboard (Données Web Scraper nettoyées)
elif menu == "📊 Dashboard des données nettoyées":
    st.title("📊 Dashboard (à partir des données brutes nettoyées automatiquement)")
    try:
        df = pd.read_csv(RAW_CSV)
        # Supprimer les colonnes inutiles
        colonnes_supprimer = [
            'web-scraper-order', 'web-scraper-start-url',
            'containers_links', 'containers_links-href'
        ]
        df.drop(columns=[col for col in colonnes_supprimer if col in df.columns], inplace=True)
        # Nettoyer les adresses
        if 'adresse' in df.columns:
            df['adresse'] = df['adresse'].astype(str).str.replace(",", "/", regex=False)

        # Nettoyer la colonne prix
        if 'prix' in df.columns:
            df['prix'] = df['prix'].astype(str)
            df['prix'] = df['prix'].str.extract(r'(\d[\d\s]*)')  
            df['prix'] = df['prix'].str.replace(" ", "", regex=False) 
            df['prix'] = pd.to_numeric(df['prix'], errors='coerce')  

        st.subheader("📌 Nombre total d’annonces")
        st.metric("Total", len(df))

        # Top 5 adresses
        if 'adresse' in df.columns:
            st.subheader("📍 Top 5 localisations (adresse)")
            top_adresses = df['adresse'].value_counts().head(5)
            st.bar_chart(top_adresses)

        # Répartition des types
        if 'type' in df.columns:
            st.subheader("📦 Répartition des types d’annonces")
            type_counts = df['type'].value_counts()
            st.bar_chart(type_counts)

        # Prix moyen par type de produit
        if "type" in df.columns and "prix" in df.columns:
            prix_moyen_par_type = df.groupby("type")["prix"].mean().sort_values(ascending=False)
            st.subheader("💸 Prix moyen par type")
            st.bar_chart(prix_moyen_par_type)

       
        # histogramme des prix
        if "prix" in df.columns:
            st.subheader("📈 Distribution détaillée des prix")
            fig, ax = plt.subplots(figsize=(10, 4))
            sns.boxplot(x=df["prix"], ax=ax)
            ax.set_xlabel("Prix (en CFA)")
            st.pyplot(fig)

    except Exception as e:
        st.error("❌ Impossible de charger ou traiter le fichier brut.")
        st.error(f"Erreur : {e}")


# Formulaire Kobo
elif menu == "📝 Formulaire kobo":
    st.title("📝 Formulaire kobotoolbox")
    kobo_url = "https://ee.kobotoolbox.org/x/o1vhFS8C"
    st.markdown(f"[🖊️ Remplir le formulaire Kobo]({kobo_url})")