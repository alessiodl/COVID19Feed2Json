import feedparser
import requests
from lxml import html
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from geocodifica import geocodeRegione as gcr
import os, sys
script_path = os.path.dirname(sys.argv[0])

app = Flask(__name__)
CORS(app)

# API END POINTS

# #####################################################################
# PROJECT INFO
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

# #####################################################################
# OUT OF DATE
# #####################################################################
@app.route('/data')
def retrieve_data():
    return jsonify({
        'message': 'This end point is no more in use. Please, take a look to the README page in the official GitHub repository',
        'github_readme':'https://github.com/alessiodl/COVID19Feed2Json/blob/master/README.md'
    })

# #####################################################################
# SUMMARY DATA
# #####################################################################
@app.route('/summary')
def retrieve_summary_data():
    # Date argument
    data = request.args.get('data')
    # Read data from CSV
    df = pd.read_csv('storico/summary.csv')
    # Apply filter if argument is passed
    if data:
        out_df = df[df.aggiornamento == str(data)]
    else:
        out_df = df
    # Return values
    out_df_sorted = out_df.sort_values(by='aggiornamento', ascending=False)
    values = json.loads(out_df_sorted.to_json(orient='records'))
    return jsonify(values)

# #####################################################################
# SANITARY STATE DATA
# #####################################################################
@app.route('/state')
def retrieve_state_data():
    # Date argument
    data = request.args.get('data')
    # Read data from CSV
    df = pd.read_csv('storico/trattamento.csv')
    # Apply filter if argument is passed
    if data:
        out_df = df[df.aggiornamento == str(data)]
    else:
        out_df = df
    # Return values
    out_df_sorted = out_df.sort_values(by='aggiornamento', ascending=False)
    values = json.loads(out_df_sorted.to_json(orient='records'))
    return jsonify(values)

# #####################################################################
# DISTRIBUTION DATA (BY REGION)
# #####################################################################
@app.route('/distribution/regions')
def retrieve_regions():
    # Date argument
    data = request.args.get('data')
    # Read data from CSV
    df = pd.read_csv('storico/regioni.csv')
    # Apply filter if argument is passed
    if data:
        out_df = df[df.aggiornamento == str(data)]
    else:
        out_df = df
    # Return values
    out_df_sorted = out_df.sort_values(by='aggiornamento', ascending=False)
    # Create GeoJSON output
    geojson = {'type':'FeatureCollection', 'features':[]}
    for index, row in out_df_sorted.iterrows():
        feature = {'type':'Feature','properties':{'aggiornamento':row['aggiornamento'],'numero_casi': row['numero_casi'],'regione': row['nome_regione']},'geometry':{'type':'Point','coordinates':[ row['lng'], row['lat'] ]}}
        geojson['features'].append(feature)
    return geojson

@app.route('/distribution/regions/last')
def retrieve_regions_last():
    # Read data from CSV
    df = pd.read_csv('storico/regioni.csv')
    # Create df using only last day data
    df_last = df.sort_values(['aggiornamento']).drop_duplicates('nome_regione', keep='last')
    # Create GeoJSON output
    geojson = {'type':'FeatureCollection', 'features':[]}
    for index, row in df_last.iterrows():
        feature = {'type':'Feature','properties':{
            'aggiornamento':row['aggiornamento'],'numero_casi': row['numero_casi'],'regione': row['nome_regione']},'geometry':{'type':'Point','coordinates':[ row['lng'], row['lat'] ]}}
        geojson['features'].append(feature)
    return geojson

@app.route('/distribution/regions/overview')
def retrieve_regions_overview():
    # Date argument
    data = request.args.get('data')
    # Read data from the online CSV
    df = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv")
    #imposta a zero i valori NaN
    # df_ = df.fillna(0)
    #trova tutte le colonne di tipo float
    # cols = df_.columns[df_.dtypes.eq('float')]
    # converte le colonne trovate in int
    # df_[cols] = df_[cols].astype(int)
    # #############################
    # GEOCODIFICA
    # #############################
    # df_['lng'] = pd.Series([gcr(name)[0] for name in df_.Regione.values])
    # df_['lat'] = pd.Series([gcr(name)[1] for name in df_.Regione.values])

    # Apply filter if argument is passed
    if data:
        out_df = df[df.data == str(data)]
    else:
        out_df = df

    # Create GeoJSON output
    geojson = {'type':'FeatureCollection', 'features':[]}
    for index, row in out_df.iterrows():
        feature = {'type':'Feature','properties':{
                        'aggiornamento':row['data'],
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

if __name__ == '__main__':
    app.run(debug=True)
