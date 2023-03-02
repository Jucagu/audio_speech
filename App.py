import streamlit as st
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import bs4
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
import requests
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
st.header('Esta aplicacion web es para obtener sentimientos de videos')
st.write('ingrese el link del video de youtube')
link=st.text_input('link')
try:
    st.video(link)
except ValueError:
    st.error("Por favor ingrese un link valido")
st.header('Nota')
st.write('Para que este proceso funcione, el video debe tener la transcripcion habilitada y los subtitulos desactivados')
st.header('Proceso')
st.write('Dado que este proceso se hace diractamente de la pagina de youtube, se debe tener en cuenta que el video debe tener habilitada la opcion de transcripcion')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome("chromedriver", options=chrome_options)
driver.delete_all_cookies()
driver.get(link)
time.sleep(5)
driver.get_screenshot_as_file("screen2.png")
st.image("screen2.png")
element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "ytp-subtitles-button")))
element.click()
more_action_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[2]/div/div/ytd-menu-renderer/yt-button-shape/button')))
more_action_btn.click()
driver.get_screenshot_as_file("screen3.png")
st.image("screen3.png")
open_trancript_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/ytd-app/ytd-popup-container/tp-yt-iron-dropdown/div/ytd-menu-popup-renderer/tp-yt-paper-listbox/ytd-menu-service-item-renderer[2]/tp-yt-paper-item/yt-formatted-string')))
open_trancript_btn.click()
st.text('En esta imagen confirmamos si la transcripcion si aparece')
driver.get_screenshot_as_file("screen4.png")
st.image("screen4.png")
html = driver.page_source
driver.quit()
st.header('Descargar codigo html')
st.download_button(label="Descargar", data=html, file_name='transcript.html', mime='text/html')
soup = bs4.BeautifulSoup(html)
#Ahora miremos la transcripcion
transcript = soup.find(id='segments-container').getText()
transcript=transcript.replace("\n"," ")
transcript=transcript.split("  ")
transcript=[x for x in transcript if len(x)>0]
#se escogen las posiciones impares del arreglo
minutes= transcript[0::2]
minutes=[x.replace(" ","") for x in minutes]
minutes.pop(-1)
#se escogen las posiciones pares del arreglo
text= transcript[1::2]
#se crea un dataframe con los datos
df=pd.DataFrame({'minutes':minutes,'text':text})
st.header('Transcripcion del video')
st.text('La transcripcion del video es la siguiente')
st.dataframe(df)
from transformers import pipeline
sentiment_pipeline = pipeline("sentiment-analysis")
data = df['text'].to_list()
pred=sentiment_pipeline(data)
#label de sentimiento
df['label']= [x['label'] for x in pred]
#score de sentimiento
df['score']= [x['score'] for x in pred]
df['transformation']=df['label'].apply(lambda x: 1 if x=='POSITIVE' else -1)
df['transformation']=df['transformation']*(df['score']-0.5)
st.header('Sentimientos del video')
st.text('Los sentimientos del video son los siguientes')
st.dataframe(df)
st.header('Grafico de sentimientos')
st.text('El grafico de sentimientos es el siguiente')
st.line_chart(data=df, x='minutes', y='transformation', width=0, height=0, use_container_width=True)
st.header('Versos mas positivos')
st.text('Los versos mas positivos son los siguientes')
st.dataframe(df.sort_values(by='transformation',ascending=False).head(5))
st.header('Versos mas negativos')
st.text('Los versos mas negativos son los siguientes')
st.dataframe(df.sort_values(by='transformation',ascending=True).head(5))

