from bs4 import BeautifulSoup
import requests
import pandas as pd
import time

# --- 1. Variables básicas ---
usuario = "SilentStorm63"
base_url = f"https://www.backloggd.com/u/{usuario}/games/?page="
pagina = 1

todos_los_juegos = []

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

    if not bloques_juegos:
        print(f"✅ No se encontraron más juegos en página {pagina}. Fin del scraping.")
        break  # No hay más juegos
    
    juegos_encontrados_en_pagina = 0

    for bloque in bloques_juegos:
        try:
            link_element = bloque.find('a', class_='cover-link')
            nombre_element = bloque.find('div', class_='game-text-centered')

            if link_element and nombre_element:
                url_relativa = link_element.get('href')
                url_juego = "https://www.backloggd.com" + url_relativa
                nombre_juego = nombre_element.get_text(strip=True)

                todos_los_juegos.append({
                    "Juego": nombre_juego,
                    "URL": url_juego
                })
                juegos_encontrados_en_pagina += 1
        except Exception as e:
            print(f"⚠️ Error leyendo un juego: {e}")

    if juegos_encontrados_en_pagina == 0:
        print(f"✅ Página {pagina} no contiene juegos nuevos. Fin del scraping.")
        break

    pagina += 1
    time.sleep(1)  # pequeña pausa para no sobrecargar el servidor

# --- 3. Guardar en Excel ---
df = pd.DataFrame(todos_los_juegos)
df.to_excel("backloggd_juegos_completo.xlsx", index=False)

df.head()
print(f"✅ ¡Scraping completo! Juegos encontrados: {len(df)}")
