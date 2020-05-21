from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import logging
import requests
import json
import numpy as np
import pandas as pd
import geopandas as gpd
import os,sys
from datetime import datetime, timedelta

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
    # exlude not georeferenced data
    df_ = df[df['lat'] != 0]
    gdf = gpd.GeoDataFrame(df_, geometry=gpd.points_from_xy(df_.long, df_.lat))
    # Out GeoJSON result
    out_geojson = json.loads(gdf.to_json())
    return jsonify(out_geojson)


@app.route('/regioni/map')
def get_regioni_map():
    # Date argument
    data = request.args.get('data')
    codice_regione = request.args.get('cod_reg')
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
        if codice_regione:
            df = df[df['codice_regione'] == int(codice_regione) ]
        daily_df = df[df['data'].str.contains(data)]
        # Change codice_regione from 4 to 41 and 42 for trento and bolzano to permit a correct join
        daily_df.loc[daily_df['denominazione_regione'].str.contains("Trento"), ["codice_regione"]] = 41
        daily_df.loc[daily_df['denominazione_regione'].str.contains("Bolzano"), ["codice_regione"]] = 42
        # Merge dataframes to obtain one complete geodataframe
        out_gdf = gdf.merge(daily_df, on='codice_regione')
        # Rename density field
        out_gdf.rename(columns = {"popKmq2011": "pop_kmq_2011"}, inplace = True)
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
    # Apply filters if arguments are passed
    if data:
        df = df[df['data'].str.contains(data)]
    if codice_regione:
        df = df[df['codice_regione'] == int(codice_regione) ]
    if codice_provincia:
        df = df[df['codice_provincia'] == int(codice_provincia)]
    if sigla_provincia:
        df = df[df['sigla_provincia'] == str(sigla_provincia)]
    # exlude 'In fase di definizione/aggiornamento' where sigla_provincia is empty
    df_ = df[df['lat'] != 0]
    gdf = gpd.GeoDataFrame(df_, geometry=gpd.points_from_xy(df_.long, df_.lat))
    # Out GeoJSON result
    out_geojson = json.loads(gdf.to_json())
    return jsonify(out_geojson)

@app.route('/province/map')
def get_province_map():
    # Date argument
    data = request.args.get('data')
    codice_regione = request.args.get('cod_reg')
    # Apply filter if argument is passed
    if data:
        # Read Local GeoJSON
        gdf = gpd.read_file('static/geo/prov_simple.shp')
        # Rename GDF fields in accord with DPC field names
        gdf.rename(columns = {"COD_PROV": "codice_provincia"}, inplace = True)
        # Read DPC CSV
        df = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv")
        if codice_regione:
            df = df[df['codice_regione'] == int(codice_regione) ]
        # exlude 'In fase di definizione/aggiornamento' where sigla_provincia is empty
        df_ = df[df['lat'] != 0]
        daily_df = df_[df_['data'].str.contains(data)]
        # Merge dataframes to obtain one complete geodataframe
        out_gdf = gdf.merge(daily_df, on='codice_provincia')
        # Rename density field
        out_gdf.rename(columns = {"popKmq2011": "pop_kmq_2011"}, inplace = True)
        # Delete unuseful or redundant columns
        out_gdf.drop(columns=['SIGLA','COD_REG','DEN_PROV','lat','long','stato'],inplace=True)
        # Out GeoJSON result
        out_geojson = json.loads(out_gdf.to_json())
        return jsonify(out_geojson)
    else:
        return jsonify({'meggage':'The \'data\' parameter is mandatory!'})

##########################################################################
# DISTRIBUTION DATA: COMUNI 
##########################################################################
@app.route('/comuni')
def get_comuni():
    # Arguments
    data = request.args.get('data')
    sigla_provincia = request.args.get('sigla_prov')
    codice_istat = request.args.get('cod_istat')
    # Read IZSAM CSV
    try:
        # print('charcode: utf-8')
        df = pd.read_csv("https://raw.githubusercontent.com/IZSAM-StatGIS/COVID19-Abruzzo/master/izs-dati/COVID_IZSAM.csv")
    except:
        # print('charcode: Windows-1252')
        df = pd.read_csv("https://raw.githubusercontent.com/IZSAM-StatGIS/COVID19-Abruzzo/master/izs-dati/COVID_IZSAM.csv",encoding='Windows-1252')
    # Apply filter if arguments are passed
    if data:
        df = df[df['DATA_TAMPONE'].str.contains(data)]
    if sigla_provincia:
        list_sigla_provincia = sigla_provincia.split(',')
        df = df[df['PROVINCIA'].isin(list_sigla_provincia)]
    if codice_istat:
        df = df[df['CODICE_ISTAT_COMUNE'] == int(codice_istat)]
    # Sort by number of cases
    df = df.sort_values(by='DATA_TAMPONE', ascending=False)
    # Out GeoJSON result
    out_geojson = json.loads(df.to_json(orient='records'))
    return jsonify(out_geojson)

@app.route('/comuni/map')
def get_comuni_map():
    # Esito arguments - mandatory
    esito = request.args.get('esito')
    # ISTAT arguments - optional
    data = request.args.get('data')
    sigla_provincia = request.args.get('sigla_prov')
    codice_istat = request.args.get('cod_istat')
    if data:
        # Read Local Shapefile
        gdf = gpd.read_file('static/geo/comuni_abruzzo_simple.shp')
        # Delete and Rename some GDF fields 
        gdf.drop(columns=['COMUNE','SIGLA_PROV'], inplace=True)
        gdf.rename(columns = {"COD_ISTAT": "CODICE_ISTAT"}, inplace = True)
        # Read IZS CSV
        df = pd.read_csv("https://raw.githubusercontent.com/IZSAM-StatGIS/COVID19-Abruzzo/master/izs-dati/ESITI_COMUNE_TOT.csv")
        # Apply mandatory data filter
        # N.B. Se il dato dei comuni non è stato ancora aggiornato l'end point ritorna i dati del giorno precedente a quello richiesto
        found_data = df[df['AGGIORNAMENTO'].str.contains(data)].index.tolist()
        if len(found_data) > 0:
            df = df[df['AGGIORNAMENTO'].str.contains(data)]
        else:
            requested_date = datetime.strptime(data, '%Y-%m-%d')
            before_date = requested_date - timedelta(1)
            before_date_str = before_date.strftime('%Y-%m-%d')
            df = df[df['AGGIORNAMENTO'].str.contains(before_date_str)]
        # Apply filter if argument is passed
        if sigla_provincia:
            df = df[df['PROVINCIA'] == sigla_provincia]
        if codice_istat:
            df = df[df['CODICE_ISTAT'] == int(codice_istat)]
        # Merge dataframes to obtain one complete geodataframe
        out_gdf = gdf.merge(df, on='CODICE_ISTAT')
        # Rename density field
        out_gdf.drop_duplicates(inplace=True)
        # Out GeoJSON result
        out_geojson = json.loads(out_gdf.to_json())
        return jsonify(out_geojson)
    else:
        return jsonify({'meggage':'The \'data\' parameter is mandatory!'}) 
    
##########################################################################
# AGGREGATIONS: ASL ABRUZZO
##########################################################################
@app.route('/esiti/asl/totals')
def get_esiti_asl_totals():
    try:
        df = pd.read_csv("https://raw.githubusercontent.com/IZSAM-StatGIS/COVID19-Abruzzo/master/izs-dati/ESITI_ASL_TOT_LATEST.csv")    
    except:
        df = pd.read_csv("https://raw.githubusercontent.com/IZSAM-StatGIS/COVID19-Abruzzo/master/izs-dati/ESITI_ASL_TOT_LATEST.csv", encoding='Windows-1252')  

    out_json = json.loads(df.to_json(orient='records'))
    return jsonify(out_json)

@app.route('/esiti/asl/daily')
def get_esiti_asl_daily():
    # Optional Arguments
    asl = request.args.get('asl')
    try:
        df = pd.read_csv("https://raw.githubusercontent.com/IZSAM-StatGIS/COVID19-Abruzzo/master/izs-dati/ESITI_ASL_GIORNALIERI_LATEST.csv")
    except:
        df = pd.read_csv("https://raw.githubusercontent.com/IZSAM-StatGIS/COVID19-Abruzzo/master/izs-dati/ESITI_ASL_GIORNALIERI_LATEST.csv", encoding='Windows-1252')

    if asl:
        list_asl = asl.split(',')
        df = df[df['ASL_RICHIEDENTE'].isin(list_asl)]
        
    out_json = json.loads(df.to_json(orient='records'))
    return jsonify(out_json)

##########################################################################
# AGGREGATIONS: PROVINCE ABRUZZO
##########################################################################
@app.route('/esiti/prov/daily')

def get_esiti_prov_daily():
    # Optional Arguments
    prov  = request.args.get('sigla_prov')
    try:
        df = pd.read_csv("https://raw.githubusercontent.com/IZSAM-StatGIS/COVID19-Abruzzo/master/izs-dati/ESITI_PROV_GIORNALIERI_LATEST.csv")
    except:
        df = pd.read_csv("https://raw.githubusercontent.com/IZSAM-StatGIS/COVID19-Abruzzo/master/izs-dati/ESITI_PROV_GIORNALIERI_LATEST.csv", encoding='Windows-1252')
    
    if prov:
        list_prov = prov.split(',')
        df = df[df['PROVINCIA'].isin(list_prov)]

    out_json = json.loads(df.to_json(orient='records'))
    return jsonify(out_json)

##########################################################################
# HOSPITALS DATA: NOT OFFICIAL!
##########################################################################
@app.route('/ospedali/covid19')
def get_covid19_hospitals():
    # Arguments
    codice_regione = request.args.get('cod_reg')
    # Read DPC CSV
    df = pd.read_csv("static/ospedali/ospedali_COVID19.csv")
    # Apply filter if argument is passed
    if codice_regione:
        df = df[df['codice_regione'] == int(codice_regione)]
        
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.long, df.lat))
    # Out GeoJSON result
    out_geojson = json.loads(gdf.to_json())
    return jsonify(out_geojson)

@app.route('/ospedali/covid19/post')
def get_covid19_hospitals_post():
    # Arguments
    codice_regione = request.args.get('cod_reg')
    # Read DPC CSV
    df = pd.read_csv("static/ospedali/ospedali_COVID19_post_acuzie.csv")
    # Apply filter if argument is passed
    if codice_regione:
        df = df[df['codice_regione'] == int(codice_regione)]
        
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.long, df.lat))
    # Out GeoJSON result
    out_geojson = json.loads(gdf.to_json())
    return jsonify(out_geojson)

@app.route('/ospedali/covid19/altri')
def get_covid19_hospitals_other():
    # Arguments
    codice_regione = request.args.get('cod_reg')
    # Read DPC CSV
    df = pd.read_csv("static/ospedali/ospedali_COVID19_altre_strutture.csv")
    # Apply filter if argument is passed
    if codice_regione:
        df = df[df['codice_regione'] == int(codice_regione)]
        
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.long, df.lat))
    # Out GeoJSON result
    out_geojson = json.loads(gdf.to_json())
    return jsonify(out_geojson)


if __name__ == '__main__':
    app.run(debug=True)
