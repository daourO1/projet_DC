import streamlit as st
import pandas as pd
import os
import subprocess

# Fichiers CSV
RAW_CSV = "donnees/webscraper_bruts.csv"
CLEAN_CSV = "donnees/webscraper_nettoyes.csv"
SCRAPED_CSV = "donnees/coinafrique_nettoye.csv"
KOBO_URL = "https://ee.kobotoolbox.org/x/o1vhFS8C"  

st.set_page_config(page_title="CoinAfrique Scraper", layout="wide")

# Menu
menu = st.sidebar.selectbox(
    "Menu",
    ["🏠 Accueil", "🕸️ Scraper CoinAfrique (BeautifulSoup)", "🧼 Voir données brutes WebScraper",
     "📊 Dashboard des données nettoyées", "📋 Formulaire d'évaluation"]
)

# Nettoyage

def clean_dataframe(df):
    colonnes_supprimer = [
        'web-scraper-order', 'web-scraper-start-url',
        'containers_links', 'containers_links-href'
    ]
    df.drop(columns=[col for col in colonnes_supprimer if col in df.columns], inplace=True)

    if 'adresse' in df.columns:
        df['adresse'] = df['adresse'].astype(str).str.replace(",", "/", regex=False)

    if 'prix' in df.columns:
        df['prix'] = df['prix'].astype(str)
        df['prix'] = df['prix'].str.extract(r'(\d[\d\s]*)')
        df['prix'] = df['prix'].str.replace(" ", "", regex=False)
        df['prix'] = pd.to_numeric(df['prix'], errors='coerce')

    return df

# Pages
if menu == "🏠 Accueil":
    st.title("Bienvenue sur l'application CoinAfrique")
    st.markdown("""
        Cette application vous permet de :
        - Scraper les données du site CoinAfrique (vêtements, chaussures, etc.)
        - Visualiser les données Web Scraper
        - Explorer un tableau de bord interactif
        - Soumettre un formulaire d'évaluation via Kobo
    """)

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
                    df = pd.read_csv(SCRAPED_CSV)
                    st.write(f"Nombre de lignes : {len(df)}")
                    st.dataframe(df)
                    st.download_button("📥 Télécharger ces données", df.to_csv(index=False), "coinafrique_nettoye.csv")
                except Exception as e:
                    st.error(f"Erreur lors de l'affichage des données : {e}")
            else:
                st.error("❌ Une erreur est survenue pendant le scraping.")
                st.code(result.stdout)
                st.code(result.stderr)

        except Exception as e:
            st.error(f"Erreur : {e}")

elif menu == "🧼 Voir données brutes WebScraper":
    st.title("📥 Données brutes depuis WebScraper")
    try:
        df = pd.read_csv(RAW_CSV)
        st.write(f"Nombre de lignes : {len(df)}")
        st.dataframe(df)
        st.download_button("📥 Télécharger les données brutes", df.to_csv(index=False), "webscraper_bruts.csv")
    except FileNotFoundError:
        st.warning("Aucun fichier WebScraper trouvé.")


elif menu == "📊 Dashboard des données nettoyées":
    st.title("📊 Tableau de bord des données Web Scraper Nettoyées")
    try:
        df = pd.read_csv(CLEAN_CSV)
        df = clean_dataframe(df)
        st.write(f"Nombre de lignes : {len(df)}")

        # Filtres
        types = st.multiselect("Filtrer par type :", options=df['type'].unique())
        if types:
            df = df[df['type'].isin(types)]

        villes = st.multiselect("Filtrer par adresse (ville) :", options=df['adresse'].unique())
        if villes:
            df = df[df['adresse'].isin(villes)]

        st.dataframe(df)
        st.download_button("📥 Télécharger les données filtrées", df.to_csv(index=False), "webscraper_bruts.csv")

        # --- Affichage des graphiques ---

        if not df.empty:

            # Distribution du nombre d'annonces par type
            st.subheader("Nombre d'annonces par type")
            counts_type = df['type'].value_counts()
            st.bar_chart(counts_type)

            # Distribution du nombre d'annonces par adresse
            st.subheader("Nombre d'annonces par adresse")
            counts_adresse = df['adresse'].value_counts().head(10)  # top 10 adresses
            st.bar_chart(counts_adresse)

            # Prix moyen par type (si la colonne 'prix' existe)
            if 'prix' in df.columns:
                df['prix'] = pd.to_numeric(df['prix'], errors='coerce')
                st.subheader("Prix moyen par type")
                prix_moyen = df.groupby('type')['prix'].mean().sort_values(ascending=False)
                st.bar_chart(prix_moyen)

        else:
            st.info("Aucune donnée à afficher après filtrage.")

    except FileNotFoundError:
        st.warning("Aucun fichier nettoyé trouvé.")


elif menu == "📋 Formulaire d'évaluation":
    st.title("📋 Lien vers le formulaire")
    st.markdown(f"Veuillez remplir le formulaire ici : [Lien Kobo]({KOBO_URL})")
