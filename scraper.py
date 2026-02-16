import os
import requests
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN ---
URL = os.environ.get("CARD_URL")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")
API_KEY = os.environ.get("SCRAPER_API_KEY")

def check_price():
    print("Iniciando scraper a través de API proxy...")
    
# Imprimimos los primeros caracteres de la URL para verificar que el Secret está bien
    # (Si pone "None" o sale con comillas, el Secret está mal configurado)
    print(f"URL objetivo: {str(URL)[:40]}...")

    # Configuramos la petición a ScraperAPI
    payload = {
        'api_key': API_KEY,
        'url': URL,
        'keep_headers': 'true',
        'country_code': 'eu' # <-- ¡CLAVE! Forzamos a usar IPs de Europa
    }
    
    # Hacemos la petición a la API
    print("Conectando con el proxy (IP Europea) para evadir Cloudflare...")
    response = requests.get('https://api.scraperapi.com/', params=payload)
    
    if response.status_code != 200:
        print(f"❌ Error {response.status_code}: La API proxy falló o fue bloqueada.")
        return

    print("✅ Conexión exitosa. Analizando el HTML...")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Buscamos el dt exacto
    etiqueta_titulo = soup.find('dt', string=lambda text: text and 'Precio medio 1 dia' in text)
    
    if etiqueta_titulo:
        etiqueta_valor = etiqueta_titulo.find_next_sibling('dd')
        
        if etiqueta_valor:
            span_precio = etiqueta_valor.find('span')
            
            if span_precio:
                precio_actual = span_precio.text.strip()
                print(f"🎯 ¡Precio encontrado! {precio_actual}")
                send_notification(precio_actual)
            else:
                print("❌ No se encontró el <span> dentro del <dd>")
        else:
            print("❌ No se encontró el valor (<dd>)")
    else:
        print("❌ No se encontró la etiqueta 'Precio medio 1 dia'")

def send_notification(price):
    print("Enviando notificación al iPhone...")
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}",
                      data=f"Nueva venta detectada. Último precio medio: {price}".encode('utf-8'),
                      headers={"Title": "Alerta One Piece Cardmarket", "Tags": "pirate_flag"})
        print("📱 ¡Notificación enviada!")
    except Exception as e:
        print(f"❌ Error al enviar: {e}")

if __name__ == "__main__":
    check_price()
