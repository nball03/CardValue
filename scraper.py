import os
import requests
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN ---
URL = os.environ.get("CARD_URL").strip()
NTFY_TOPIC = os.environ.get("NTFY_TOPIC").strip()
API_KEY = os.environ.get("SCRAPER_API_KEY").strip()

# Archivo donde guardaremos la "memoria" del bot
ARCHIVO_PRECIO = "ultimo_precio.txt"

def leer_ultimo_precio():
    if os.path.exists(ARCHIVO_PRECIO):
        with open(ARCHIVO_PRECIO, "r") as file:
            return file.read().strip()
    return None # Si es la primera vez que se ejecuta, no hay precio guardado

def guardar_nuevo_precio(precio):
    with open(ARCHIVO_PRECIO, "w") as file:
        file.write(precio)

def check_price():
    print("Iniciando scraper a través de API proxy...")
    
    payload = {
        'api_key': API_KEY,
        'url': URL,
        'country_code': 'eu',
        'render': 'true'
    }
    
    print("Conectando con el proxy (IP Europea + Render JS)...")
    response = requests.get('https://api.scraperapi.com/', params=payload)
    
    if response.status_code != 200:
        print(f"❌ Error {response.status_code}: La API proxy falló o fue bloqueada.")
        return

    print("✅ Conexión exitosa. Analizando el HTML...")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    etiqueta_titulo = soup.find('dt', string=lambda text: text and 'Precio medio 1 dia' in text)
    
    if etiqueta_titulo:
        etiqueta_valor = etiqueta_titulo.find_next_sibling('dd')
        if etiqueta_valor:
            span_precio = etiqueta_valor.find('span')
            if span_precio:
                precio_actual = span_precio.text.strip()
                print(f"🎯 Precio encontrado en la web: {precio_actual}")
                
                # --- LA MAGIA: COMPARAMOS CON LA MEMORIA ---
                ultimo_precio = leer_ultimo_precio()
                print(f"🧠 Precio en memoria: {ultimo_precio}")
                
                if precio_actual != ultimo_precio:
                    print("⚠️ ¡EL PRECIO HA CAMBIADO! Enviando notificación...")
                    send_notification(precio_actual, ultimo_precio)
                    guardar_nuevo_precio(precio_actual)
                else:
                    print("💤 El precio sigue igual. No se envía notificación.")
                    
            else:
                print("❌ No se encontró el <span> dentro del <dd>")
        else:
            print("❌ No se encontró el valor (<dd>)")
    else:
        print("❌ No se encontró la etiqueta 'Precio medio 1 dia'")

def send_notification(precio_actual, precio_anterior):
    print("Enviando notificación al iPhone...")
    
    # Preparamos un mensaje distinto si es la primera vez
    if precio_anterior is None:
        mensaje = f"Primera lectura registrada. Precio inicial: {precio_actual}"
        titulo = "🟢 Tracker Inicializado"
    else:
        mensaje = f"El precio ha cambiado de {precio_anterior} a {precio_actual}"
        titulo = "⚠️ Alerta One Piece Card"

    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}",
                      data=mensaje.encode('utf-8'),
                      headers={"Title": titulo, "Tags": "pirate_flag,chart_with_upwards_trend"})
        print("📱 ¡Notificación enviada!")
    except Exception as e:
        print(f"❌ Error al enviar: {e}")

if __name__ == "__main__":
    check_price()
