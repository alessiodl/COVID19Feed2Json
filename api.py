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
        feature = {'type':'Feature','properties':{'aggiornamento':row['aggiornamento'],'numero_casi': row['numero_casi'],'regione': row['nome_regione']},'geometry':{'type':'Point','coordinates':[ row['lng'], row['lat'] ]}}
        geojson['features'].append(feature)
    return geojson

if __name__ == '__main__':
    app.run(debug=True)
