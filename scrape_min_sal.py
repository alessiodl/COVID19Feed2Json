import requests
from lxml import html
import re
import csv
import pandas as pd
from geocodifica import geocodeRegione
from estrazione_data import formatDate
from salva_storico import saveSummary, saveTreatments, saveRegions
import os, sys

# PATH
script_path = os.path.dirname(sys.argv[0])
storico_path = os.path.join(script_path,'storico')
csv_summary = os.path.join(storico_path,'summary.csv')
csv_trattamento = os.path.join(storico_path,'trattamento.csv')
csv_regioni = os.path.join(storico_path,'regioni.csv')

# ORIGINE: MINISTERO DELLA SALUTE
# ############################################################################
url = "http://www.salute.gov.it/portale/nuovocoronavirus/dettaglioContenutiNuovoCoronavirus.jsp?lingua=italiano&id=5351&area=nuovoCoronavirus&menu=vuoto"
resp = requests.get(url)
tree = html.fromstring(resp.content)

# TITOLO
# ############################################################################
titolo = tree.xpath("//h4[@class='blu-italia-base-color']//text()")[0].strip()
print(titolo)

# DATA DI AGGIORNAMENTO
# ############################################################################
data = formatDate(titolo)

# POSITIVI, DECEDUTI, GUARITI, CASI
# ############################################################################
positivi = tree.xpath('.//div/span[contains(text(),"POSITIVI")]/following::div[1]/text()')[0].strip()
deceduti = tree.xpath('.//div/span[contains(text(),"DECEDUTI")]/following::div[1]/text()')[0].strip()
guariti  = tree.xpath('.//div/span[contains(text(),"GUARITI")]/following::div[1]/text()')[0].strip()
tot_casi = int(positivi)+int(deceduti)+int(guariti)
# Salvataggio nello storico
saveSummary(data, positivi, deceduti, guariti, tot_casi, csv_summary)

# POSITIVI IN ISOLAMENTO DOMICILIARE, RICOVERATI CON SINTOMI, TERAPIA INTENSIVA
# ############################################################################
isolamento_domiciliare = tree.xpath('.//h3[contains(text(),"Covid-19 - Situazione in Italia")]/following::p[2]/following::ul[2]/li[contains(text(),"isolamento domiciliare")]/text()')
ricoverati_con_sintomi = tree.xpath('.//h3[contains(text(),"Covid-19 - Situazione in Italia")]/following::p[2]/following::ul[2]/li[contains(text(),"ricoverati con sintomi")]/text()')
terapia_intensiva = tree.xpath('.//h3[contains(text(),"Covid-19 - Situazione in Italia")]/following::p[2]/following::ul[2]/li[contains(text(),"terapia intensiva")]/text()')

num_isolamento = int(re.findall(r'\d+', isolamento_domiciliare[0].strip())[0])
num_ricoverati = int(re.findall(r'\d+', ricoverati_con_sintomi[0].strip())[0])
num_tintensiva = int(re.findall(r'\d+', terapia_intensiva[0].strip())[0])
# Salvataggio nello storico
saveTreatments(data, num_isolamento, num_ricoverati, num_tintensiva, csv_trattamento)

# DATI REGIONE PER REGIONE
# NOTA: 
# ** 
#   DAL 3 MARZO IL MINISTERO NON PUBBLICA PIU' SUL SITO IL RIEPILOGO
#   REGIONALE. QUESTO STEP DELLO SCRAPING E' QUINDI DIVENTATO INUTILE.
#   IL RIEPILOGO REGIONALE VIENE LETTO DIRETTAMENTE DAL REPO DI ANDREA BORRUSO
#   CHE LO AGGIORNA A PARTIRE DAL PDF MINISTERIALE OGNI SERA INTORNO ALLE 18:30.
#   LO STORICO PREGRESSO CREATO DA QUESTO SCRAPING VIENE COMUNQUE MANTENUTO
# **
# ############################################################################
'''
regioni = tree.xpath("//div/p/strong[.='Regioni']/following::ul[1]/li//text()")
list_regioni = []
df = pd.read_csv(csv_regioni)
for regione in regioni:
    # data_aggiornamento = titolo.split(":")[1].strip()
    aggiornamento = str(data)
    num_casi = re.findall(r'\d+',regione)[0]
    nome_regione = regione.strip().replace(num_casi,'').replace('.','')
    coordinates = geocodeRegione(nome_regione)
    lng = str(coordinates[0])
    lat = str(coordinates[1])
    #print('aggiornamento;num_casi;nome_regione;lng;lat;')
    #print(aggiornamento+","+num_casi+","+nome_regione+","+lng+","+lat)
    list_regioni.append(pd.Series([aggiornamento, num_casi, nome_regione, lng, lat], index=df.columns ))
# Salvataggio nello storico
saveRegions(list_regioni,data,csv_regioni)

'''

    
