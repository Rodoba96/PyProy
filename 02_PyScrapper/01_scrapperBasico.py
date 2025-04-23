import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

usuario = "SilentStorm63"
listas = ["games", "played", "completed", "backlog", "wishlist", "favorites"]
base_url = f"https://www.backloggd.com/u/{usuario}/games"
resultados = []

headers = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_lista(lista):
    page = 1
    while True:
        if lista == "games":
            url = f"{base_url}/?page={page}"
            lista_nombre = "All"
        else:
            url = f"{base_url}/{lista}/?page={page}"
            lista_nombre = lista.capitalize()
        
        print(f"Scrapeando: {lista_nombre} - Página {page}")
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        
        juegos = soup.select(".game-outer-container")
        if not juegos:
            break

        for juego in juegos:
            nombre = juego.select_one(".game-title").text.strip()
            link = "https://www.backloggd.com" + juego.select_one("a")["href"]
            resultados.append({
                "Juego": nombre,
                "URL": link,
                "Lista": lista_nombre
            })
        
        page += 1
        time.sleep(1.5)  # Pausa para evitar bloqueo

# Ejecutamos scraping para todas las listas
for lista in listas:
    scrape_lista(lista)

# Guardamos en DataFrame
df = pd.DataFrame(resultados).drop_duplicates(subset=["Juego", "Lista"])
df.to_excel("backloggd_juegos_basico.xlsx", index=False)
print("✅ Listas guardadas en backloggd_juegos_basico.xlsx")
