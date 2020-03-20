from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import logging
import requests
import json
import pandas as pd
import geopandas as gpd
import os,sys

app = Flask(__name__)
CORS(app)

### Logging
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

### swagger specific ###
SWAGGER_URL = '/doc'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "COVID19 API"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###

# API END POINTS

# ########################################################################
# ROOT
# ########################################################################
@app.route('/')
def hello():
    return redirect('/doc')

# ########################################################################
# GENERAL INFO
# ########################################################################
@app.route('/info')
def apiInfo():
    return jsonify({
        'author':'Alessio Di Lorenzo',
        'email':'alessio.dl@gmail.com',
        'description':'Italian Civil Protection Department and Ministry of Health official COVID19 data in Italy',
        'data_source': 'https://github.com/pcm-dpc/COVID-19',
        'project_readme':'https://github.com/alessiodl/COVID19Feed2Json/blob/master/README.md',
        'project_home':'https://github.com/alessiodl/COVID19Feed2Json'
    })

##########################################################################
# TREND DATA
##########################################################################
@app.route('/andamento')
def get_andamento():
    # Date argument
    data = request.args.get('data')
    # Read DPC CSV
    df = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv")
    df = df.sort_values(by='data', ascending=False)
    # Apply filter if argument is passed
    if data:
        # out_df = df[df.data == str(data)]
        out_df = df[df['data'].str.contains(data)]
    else:
        out_df = df
    valori = json.loads(out_df.to_json(orient='records'))
    return jsonify(valori)

##########################################################################
# DISTRIBUTION DATA: REGIONS
##########################################################################
@app.route('/regioni')
def get_regioni():
    # Date argument
    data = request.args.get('data')
    codice_regione = request.args.get('cod_reg')
    # Read DPC CSV
    df = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv")
    # Apply filters if argument are passed
    if data:
        df = df[df['data'].str.contains(data)]
    if codice_regione:
        df = df[df['codice_regione'] == int(codice_regione) ]
    # Create GeoJSON output
    geojson = {'type':'FeatureCollection', 'features':[]}
    for index, row in df.iterrows():
        # exlude not georeferenced data
        if row['long'] != 0 and row['lat'] != 0:
            feature = {'type':'Feature','properties':{
                        'data':row['data'],
                        'codice_regione': row['codice_regione'],
                        'denominazione_regione': row['denominazione_regione'],
                        'totale_casi': row['totale_casi'],
                        'ricoverati_con_sintomi': row['ricoverati_con_sintomi'],
                        'terapia_intensiva': row['terapia_intensiva'],
                        'totale_ospitalizzati': row['totale_ospedalizzati'],
                        'isolamento_domiciliare': row['isolamento_domiciliare'],
                        'totale_attualmente_positivi': row['totale_attualmente_positivi'],
                        'dimessi_guariti': row['dimessi_guariti'],
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

@app.route('/regioni/map')
def get_regioni_map():
    # Date argument
    data = request.args.get('data')
    # Apply filter if argument is passed
    if data:
        # Read Local GeoJSON
        gdf = gpd.read_file('static/geo/reg_simple.shp')
        # Rename GDF fields in accord with DPC field names
        gdf.rename(columns = {"COD_REG": "codice_regione"}, inplace = True)
        # Change codice_regione from 4 to 41 and 42 for trento and bolzano to permit a correct join
        gdf.loc[gdf['DEN_REG'] == "Trento", ["codice_regione"]] = 41
        gdf.loc[gdf['DEN_REG'] == "Bolzano", ["codice_regione"]] = 42
        # Read DPC CSV
        df = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv")
        daily_df = df[df['data'].str.contains(data)]
        # Change codice_regione from 4 to 41 and 42 for trento and bolzano to permit a correct join
        daily_df.loc[daily_df['denominazione_regione'].str.contains("Trento"), ["codice_regione"]] = 41
        daily_df.loc[daily_df['denominazione_regione'].str.contains("Bolzano"), ["codice_regione"]] = 42
        # Merge dataframes to obtain one complete geodataframe
        out_gdf = gdf.merge(daily_df, on='codice_regione')
        # Delete unuseful or redundant columns
        out_gdf.drop(columns=['DEN_REG', 'lat','long'],inplace=True)
        # Out GeoJSON result
        out_geojson = json.loads(out_gdf.to_json())
        return jsonify(out_geojson)
    else:
        return jsonify({'meggage':'The \'data\' parameter is mandatory!'})

##########################################################################
# DISTRIBUTION DATA: PROVINCES
##########################################################################
@app.route('/province')
def get_province():
    # Arguments
    data = request.args.get('data')
    codice_regione = request.args.get('cod_reg')
    codice_provincia = request.args.get('cod_prov')
    sigla_provincia = request.args.get('sigla_prov')
    # Read DPC CSV
    df = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv")
    # Apply filter if arguments are passed
    if data:
        df = df[df['data'].str.contains(data)]
    if codice_regione:
        df = df[df['codice_regione'] == int(codice_regione) ]
    if codice_provincia:
        df = df[df['codice_provincia'] == int(codice_provincia)]
    if sigla_provincia:
        df = df[df['sigla_provincia'] == str(sigla_provincia)]
    # exlude 'In fase di definizione/aggiornamento' where sigla_provincia is NaN
    df_ = df[df_['sigla_provincia'] != ""]

    # Create GeoJSON output
    geojson = {'type':'FeatureCollection', 'features':[]}
    for index, row in df_.iterrows():
        feature = {'type':'Feature','properties':{
                    'data':row['data'],
                    'stato':row['stato'],
                    'denominazione_regione': row['denominazione_regione'],
                    'codice_regione': row['codice_regione'],
                    'denominazione_provincia': row['denominazione_provincia'],
                    'sigla_provincia': row['sigla_provincia'],
                    'codice_provincia': row['codice_provincia'],
                    'totale_casi': row['totale_casi']
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

@app.route('/province/map')
def get_province_map():
    # Date argument
    data = request.args.get('data')
    # Apply filter if argument is passed
    if data:
        # Read Local GeoJSON
        gdf = gpd.read_file('static/geo/prov_simple.shp')
        # Rename GDF fields in accord with DPC field names
        gdf.rename(columns = {"COD_PROV": "codice_provincia"}, inplace = True)
        # Read DPC CSV
        df = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv")
        # exlude 'In fase di definizione/aggiornamento' where sigla_provincia is NaN
        df_ = df[df_['sigla_provincia'] != ""]
        daily_df = df_[df_['data'].str.contains(data)]
        # Merge dataframes to obtain one complete geodataframe
        out_gdf = gdf.merge(daily_df, on='codice_provincia')
        # Delete unuseful or redundant columns
        out_gdf.drop(columns=['SIGLA','COD_REG','DEN_PROV','lat','long','stato'],inplace=True)
        # Out GeoJSON result
        out_geojson = json.loads(out_gdf.to_json())
        return jsonify(out_geojson)
    else:
        return jsonify({'meggage':'The \'data\' parameter is mandatory!'})

##########################################################################
# DISTRIBUTION DATA: COMUNI (NOT OFFICIAL!)
##########################################################################
@app.route('/comuni')
def get_comuni():
    # Arguments
    data = request.args.get('data')
    codice_regione = request.args.get('cod_reg')
    codice_provincia = request.args.get('cod_prov')
    codice_istat = request.args.get('cod_istat')
    # Read DPC CSV
    df = pd.read_csv("https://raw.githubusercontent.com/alessiodl/COVID19Abruzzo/master/dati-comuni/izsam-covid19-ita-comuni.csv")
    # Apply filter if arguments are passed
    if data:
        df = df[df['data'].str.contains(data)]
    if codice_regione:
        df = df[df['codice_regione'] == int(codice_regione) ]
    if codice_provincia:
        df = df[df['codice_provincia'] == int(codice_provincia)]
    if codice_istat:
        df = df[df['codice_istat'] == int(codice_istat)]
    # Sort by number of cases
    df = df.sort_values(by='totale_casi', ascending=False)
    # Out GeoJSON result
    out_geojson = json.loads(df.to_json(orient='records'))
    return jsonify(out_geojson)

@app.route('/comuni/map')
def get_comuni_map():
    # Date argument - mandatory
    data = request.args.get('data')
    # ISTAT arguments - optional
    codice_regione = request.args.get('cod_reg')
    codice_provincia = request.args.get('cod_prov')
    codice_istat = request.args.get('cod_istat')
    # Apply filter if argument is passed
    if data:
        # Read Local GeoJSON
        gdf = gpd.read_file('static/geo/abruzzo_simple.shp')
        # Rename GDF fields in accord with DPC field names
        gdf.rename(columns = {"PRO_COM": "codice_istat"}, inplace = True)
        # Read DPC CSV
        df = pd.read_csv("https://raw.githubusercontent.com/alessiodl/COVID19Abruzzo/master/dati-comuni/izsam-covid19-ita-comuni.csv")
        daily_df = df[df['data'].str.contains(data)]
        if codice_regione:
            daily_df = daily_df[daily_df['codice_regione'] == int(codice_regione) ]
        if codice_provincia:
            daily_df = daily_df[daily_df['codice_provincia'] == int(codice_provincia)]
        if codice_istat:
            daily_df = daily_df[daily_df['codice_istat'] == int(codice_istat)]
        # Merge dataframes to obtain one complete geodataframe
        out_gdf = gdf.merge(daily_df, on='codice_istat')
        
        # Delete unuseful or redundant columns
        out_gdf.drop(columns=['COMUNE','Shape_Area','Shape_Leng'],inplace=True)
        # Out GeoJSON result
        out_geojson = json.loads(out_gdf.to_json())
        return jsonify(out_geojson)
    else:
        return jsonify({'meggage':'The \'data\' parameter is mandatory!'})


if __name__ == '__main__':
    app.run(debug=True)
