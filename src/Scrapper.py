# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 10:37:48 2024

@author: mffigarola
"""
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import time
import base64
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Crear el servicio para ChromeDriver
service = Service("C:/Users/mffigarola/OneDrive - Edenor/Documentos/chromedriver-win64/chromedriver.exe")

# Inicializar el navegador
driver = webdriver.Chrome(service=service)

# Acceder a Facebook Marketplace
driver.get('https://www.facebook.com/marketplace')

# Aquí deberías iniciar sesión si es necesario
time.sleep(30)  # Esperar para que inicies sesión manualmente o usar Selenium para llenar los datos

# Leer el archivo de Excel
df = pd.read_excel('links facebook.xlsx', sheet_name='links')

# Suponiendo que las URLs están en una columna llamada 'URL'
urls = df['URL'].tolist()  # Cambia 'URL' al nombre de la columna correcta si es diferente

# Limitar a las primeras 4 URLs (puedes ajustar este límite según lo necesites)
for idx, url in enumerate(urls):
    try:
        # Acceder a la URL específica del anuncio
        driver.get(url)
        time.sleep(5)  # Esperar a que la página cargue

        # Extraer el HTML de la página
        html = driver.page_source

        # Analizar el HTML con BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Buscar las URLs de las imágenes con la clase específica
        imagenes = soup.find_all('img', class_='xz74otr')  # Filtrar solo las imágenes con la clase 'xz74otr'
        
        # Crear una sesión de requests
        session = requests.Session()
        
        # Contador para las imágenes descargadas
        img_count = 0

        for img in imagenes:
            if img_count >= 4:  # Limitar a las primeras 4 imágenes
                break
            
            src = img.get('src')
            if src:
                # Mantener la URL original para verificar si se requiere limpieza
                original_src = src  # Guardar la URL original

                try:
                    # Para imágenes de URL, deshabilitar la verificación SSL
                    response = session.get(original_src, verify=False)  # Usar la URL original aquí
                    
                    # Verificar el tipo de contenido
                    if 'image' in response.headers['Content-Type']:
                        img_data = response.content
                        extension = original_src.split('.')[-1].split('?')[0] if '.' in original_src else 'jpg'  # Determinar la extensión del archivo
                        
                        if extension not in ['jpg', 'jpeg', 'png']:  # Asegurar que la extensión sea válida
                            extension = 'jpg'  # Asignar jpg como predeterminado

                        with open(f'imagen_{idx}_{img_count}.{extension}', 'wb') as handler:
                            handler.write(img_data)

                        img_count += 1  # Incrementar el contador de imágenes
                    else:
                        print(f"El contenido de {original_src} no es una imagen. Tipo de contenido: {response.headers['Content-Type']}")

                except requests.exceptions.RequestException as e:
                    print(f"Error al descargar la imagen {original_src}: {e}")
                except Exception as e:
                    print(f"Error inesperado al procesar la imagen {original_src}: {e}")

    except Exception as e:
        print(f"Error al procesar la URL {url}: {e}")
# Cerrar el navegador
driver.quit()