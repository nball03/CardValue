import cloudscraper
from bs4 import BeautifulSoup
import requests
import os

# Configuración (Usa variables de entorno por seguridad)
URL = os.environ.get("CARD_URL")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")

def check_price():
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    response = scraper.get(URL)
    
    if response.status_code != 200:
        print(f"Error {response.status_code}: Bloqueado por Cloudflare")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 1. Buscamos el elemento <dt> que contiene el texto exacto que precede a tu dato.
    # Nota: Asegúrate de poner el texto tal cual aparece en la web.
    etiqueta_titulo = soup.find('dt', string=lambda text: text and 'Precio medio 1 dia' in text)
    
    if etiqueta_titulo:
        # 2. Buscamos el siguiente elemento hermano (<dd>)
        etiqueta_valor = etiqueta_titulo.find_next_sibling('dd')
        
        if etiqueta_valor:
            # 3. Extraemos el texto del <span> que está dentro del <dd>
            span_precio = etiqueta_valor.find('span')
            
            if span_precio:
                precio_actual = span_precio.text.strip()
                print(f"¡Precio encontrado! {precio_actual}")
                send_notification(precio_actual)
            else:
                print("No se encontró el <span> dentro del <dd>")
    else:
        print("No se encontró la etiqueta 'Precio medio 1 dia'")

def send_notification(price):
    requests.post(f"https://ntfy.sh/{NTFY_TOPIC}",
                  data=f"Nueva actualización de precio: {price}".encode('utf-8'),
                  headers={"Title": "Alerta One Piece Card"})

if __name__ == "__main__":
    check_price()
