from bs4 import BeautifulSoup
import requests
import pandas as pd
import time

# --- 1. Variables básicas ---
usuario = "SilentStorm63"
base_url = f"https://www.backloggd.com/u/{usuario}/games/?page="
pagina = 1

todos_los_juegos = []
urls_existentes = set()

headers = {
    "User-Agent": "Mozilla/5.0"
}

# --- 2. Loop para recorrer páginas ---
while True:
    print(f"Scrapeando página {pagina}...")
    
    url = base_url + str(pagina)
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"⚠️ Error al cargar página {pagina}. Código {response.status_code}")
        break
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    bloques_juegos = soup.find_all('div', class_='rating-hover')

    juegos_nuevos_encontrados = 0  # contador de juegos nuevos

    for bloque in bloques_juegos:
        try:
            link_element = bloque.find('a', class_='cover-link')
            nombre_element = bloque.find('div', class_='game-text-centered')

            if link_element and nombre_element:
                url_relativa = link_element.get('href')
                url_juego = "https://www.backloggd.com" + url_relativa
                nombre_juego = nombre_element.get_text(strip=True)

                if url_juego not in urls_existentes:  # 🚨 solo si es realmente nuevo
                    todos_los_juegos.append({
                        "Juego": nombre_juego,
                        "URL": url_juego
                    })
                    urls_existentes.add(url_juego)
                    juegos_nuevos_encontrados += 1
        except Exception as e:
            print(f"⚠️ Error leyendo un juego: {e}")

    if juegos_nuevos_encontrados == 0:
        print(f"✅ No se encontraron juegos nuevos en página {pagina}. Fin del scraping.")
        break

    pagina += 1
    time.sleep(1)

# --- 3. Guardar en Excel ---
df = pd.DataFrame(todos_los_juegos)
df.to_excel("backloggd_juegos_completo.xlsx", index=False, engine='openpyxl')
print(f"✅ ¡Scraping completo! Juegos encontrados: {len(df)}")
print(df.head())