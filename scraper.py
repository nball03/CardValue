import cloudscraper
from bs4 import BeautifulSoup
import requests
import os

# Configuración (Usa variables de entorno por seguridad)
URL = os.getenv("CARD_URL")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")

def check_price():
    # Creamos el scraper que emula un navegador real
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    response = scraper.get(URL)
    
    if response.status_code != 200:
        print(f"Error {response.status_code}: Bloqueado por Cloudflare")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Selector CSS para el precio (esto puede variar, hay que inspeccionar el HTML)
    # Por ejemplo, el precio del artículo más barato suele estar en este selector:
    price_element = soup.select_one(".price-container .h2")
    
    if price_element:
        price = price_element.text.strip()
        send_notification(price)

def send_notification(price):
    requests.post(f"https://ntfy.sh/{NTFY_TOPIC}",
                  data=f"Nueva actualización de precio: {price}".encode('utf-8'),
                  headers={"Title": "Alerta One Piece Card"})

if __name__ == "__main__":
    check_price()
