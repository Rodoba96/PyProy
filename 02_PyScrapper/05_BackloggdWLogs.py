from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# --- CONFIGURACIÓN ---
EXCEL_ENTRADA = "backloggd_juegos_completo.xlsx"
EXCEL_SALIDA = "backloggd_juegos_con_logs.xlsx"
USUARIO = "SilentStorm63"

# --- Cargar Excel existente ---
df = pd.read_excel(EXCEL_ENTRADA)

# Añadir columnas si no existen
for col in ["Horas Jugadas", "Fecha Inicio", "Fecha Fin"]:
    if col not in df.columns:
        df[col] = ""

# --- Configurar navegador ---
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-insecure-localhost')
options.add_argument('--disable-web-security')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# --- Recorrer todos los juegos ---
for index, row in df.iterrows():
    url_original = row['URL']
    juego = row['Juego']
    
    slug = url_original.split("/games/")[-1].strip("/")
    log_url = f"https://backloggd.com/u/{USUARIO}/logs/{slug}/"

    print(f"🔍 {index+1}/{len(df)} - {juego}")
    print(f"    {log_url}")

    try:
        driver.get(log_url)
        time.sleep(2.5)

        # Horas jugadas
        try:
            reloj_icono = driver.find_element(By.CLASS_NAME, "fa-stopwatch")
            horas = reloj_icono.find_element(By.XPATH, "./..").text.strip()
        except:
            horas = ""

        # Fechas
        try:
            texto = driver.find_element(By.CLASS_NAME, "game-log-view").text
            lineas = texto.split("\n")

            fecha_inicio = ""
            fecha_fin = ""
            for i, linea in enumerate(lineas):
                if "FIRST PLAYED" in linea.upper():
                    fecha_inicio = lineas[i+1]
                if "LAST PLAYED" in linea.upper():
                    fecha_fin = lineas[i+1]
        except:
            fecha_inicio = ""
            fecha_fin = ""

        # Guardar en el DataFrame
        df.at[index, "Horas Jugadas"] = horas
        df.at[index, "Fecha Inicio"] = fecha_inicio
        df.at[index, "Fecha Fin"] = fecha_fin

    except Exception as e:
        print(f"⚠️ Error en {log_url}: {e}")

# --- Guardar nuevo Excel ---
df.to_excel(EXCEL_SALIDA, index=False)
print(f"\n✅ Archivo generado: {EXCEL_SALIDA} con {len(df)} juegos.")

# --- Cerrar navegador ---
driver.quit()
