import feedparser
import requests
from lxml import html
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os, sys
script_path = os.path.dirname(sys.argv[0])

app = Flask(__name__)
CORS(app)

# API END POINTS

# #####################################################################
# GENERAL INFO
# #####################################################################
@app.route('/')
@app.route('/info')
def retrieve_app_info():
    return jsonify({
        'author':'Alessio Di Lorenzo',
        'description':'Python API returning Italian Civil Protection Department and Ministry of Health official COVID19 data in Italy. It is based on daily web scraping activity',
        'data_source': 'Ministero della Salute',
        'project_readme':'https://github.com/alessiodl/COVID19Feed2Json/blob/master/README.md',
        'project_home':'https://github.com/alessiodl/COVID19Feed2Json',
    })

##########################################################################
# TREND DATA
##########################################################################
@app.route('/andamento')
def andamentoNazionale():
    # Date argument
    data = request.args.get('data')
    # Read DPC CSV
    df = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv")
    df = df.sort_values(by='data', ascending=False)
    # Apply filter if argument is passed
    if data:
        out_df = df[df.data == str(data)]
    else:
        out_df = df
    valori = json.loads(out_df.to_json(orient='records'))
    return jsonify(valori)

##########################################################################
# DISTRIBUTION DATA: REGIONS
##########################################################################
@app.route('/regioni')
def retrieve_regions_overview():
    # Date argument
    data = request.args.get('data')
    # Read DPC CSV
    df = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv")
    # Apply filter if argument is passed
    if data:
        out_df = df[df.data == str(data)]
    else:
        out_df = df
    # Create GeoJSON output
    geojson = {'type':'FeatureCollection', 'features':[]}
    for index, row in out_df.iterrows():
        # exlude not georeferenced data
        if row['long'] != 0 and row['lat'] != 0:
            feature = {'type':'Feature','properties':{
                        'data':row['data'],
                        'regione': row['denominazione_regione'],
                        'numero_casi': row['totale_casi'],
                        'ricoverati_con_sintomi': row['ricoverati_con_sintomi'],
                        'terapia_intensiva': row['terapia_intensiva'],
                        'terapia_intensiva': row['totale_ospedalizzati'],
                        'isolamento_domiciliare': row['isolamento_domiciliare'],
                        'totale_positivi': row['totale_attualmente_positivi'],
                        'guariti': row['dimessi_guariti'],
                        'deceduti': row['deceduti'],
                        'tamponi': row['tamponi']
                        },
                        'geometry':{
                            'type':'Point',
                            'coordinates':[ 
                                row['long'], row['lat'] 
                            ]
                        }
                    }
            geojson['features'].append(feature)
    return geojson

##########################################################################
# DISTRIBUTION DATA: PROVINCES
##########################################################################
@app.route('/province')
def distribProvince():
    # Arguments
    data = request.args.get('data')
    codice_regione = request.args.get('codice_regione')
    codice_provincia = request.args.get('codice_provincia')
    # Read DPC CSV
    df = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv")
    # Apply filter if argument is passed
    if data:
        out_df = df[df.data == str(data)]
    else:
        out_df = df
    
    # exlude 'In fase di definizione/aggiornamento' where sigla_provincia is NaN
    df_ = out_df[out_df['sigla_provincia'].notna()]

    # Create GeoJSON output
    geojson = {'type':'FeatureCollection', 'features':[]}
    for index, row in df_.iterrows():
        feature = {'type':'Feature','properties':{
                    'data':row['data'],
                    'stato':row['stato'],
                    'regione': row['denominazione_regione'],
                    'regione_codice': row['codice_regione'],
                    'provincia': row['denominazione_provincia'],
                    'provincia_sigla': row['sigla_provincia'],
                    'provincia_codice': row['codice_provincia'],
                    'numero_casi': row['totale_casi']
                    },
                    'geometry':{
                            'type':'Point',
                            'coordinates':[ 
                                row['long'], row['lat'] 
                            ]
                        }
                    }
        geojson['features'].append(feature)
    return geojson

if __name__ == '__main__':
    app.run(debug=True)
