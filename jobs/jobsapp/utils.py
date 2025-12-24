from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from .models import JobOffre

def scrape_novojob_selenium():
    base_url = "https://www.novojob.com"
    url = f"{base_url}/cote-d-ivoire/offres-d-emploi?collapsed=PROFESSION"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    offres = soup.find_all("li", class_="separator-bot")

    for offre in offres:
        titre = offre.find("h2", class_="ellipsis row-fluid")
        titre_texte = titre.get_text(strip=True) if titre else "Titre non disponible"

        lien_tag = offre.find("a")
        lien = lien_tag['href'] if lien_tag and lien_tag.has_attr("href") else None
        lien_complet = base_url + lien if lien and lien.startswith("/") else lien

        entreprise = offre.find("h6", class_="ellipsis")
        entreprise_nom = entreprise.get_text(strip=True) if entreprise else "Entreprise non précisée"

        lieu = offre.find("span", class_="spaced-right")
        lieu_texte = lieu.get_text(strip=True) if lieu else "Lieu non précisé"

        date_expiration = "Date non trouvée"
        description = "Description non trouvée"

        if lien_complet:
            try:
                driver.get(lien_complet)
                time.sleep(1.5)
                offer_soup = BeautifulSoup(driver.page_source, "html.parser")

                infos = offer_soup.find_all("li", class_="row-fluid")
                for info in infos:
                    label = info.find("span", class_="span4 text-bold")
                    value = info.find("span", class_="span8")
                    if label and value and "Date d'expiration" in label.text:
                        date_expiration = value.get_text(strip=True)
                        break

                content_div = offer_soup.find("div", class_="spaced details-description")
                if content_div:
                    description = content_div.get_text(separator="\n", strip=True)

            except Exception as e:
                print("Erreur en accédant à :", lien_complet)
                print(e)

        
        JobOffre.objects.update_or_create(
            url=lien_complet,
            defaults={
                "title": titre_texte,
                "company": entreprise_nom,
                "location": lieu_texte,
                "expiration_date": date_expiration,
                "description": description,
                "domain": "",  
            }
        )

    driver.quit()
