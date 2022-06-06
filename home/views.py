import genericpath
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from home.models import *
from django.views import generic
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import io
import base64
import urllib, json
from django.conf import settings as django_settings
import os
from django.contrib.staticfiles.storage import staticfiles_storage
from collections import defaultdict

def go_index(request):
    template_name = 'index.html'
    
    features = Features.objects.all()
    df_features = pd.DataFrame(list(Features.objects.all().values()))
    url = "https://drive.google.com/file/d/1oJxlSRVp11C-M9vyBraGuuyHxlpQWVgT/view?usp=sharing"
    countries  = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]
    
    response = urllib.request.urlopen(countries)
    
    input_dict = json.loads(response.read())
    output_json = json.dumps(input_dict)

    
    iso_eu = df_features['code']
    
    iso_dict = [{'iso': u}
        for u in iso_eu]

    output_iso = json.dumps(iso_dict)

    return render(request,'index.html', {'features' : features,"json_map": output_json, "country_codes": output_iso})
    
def go_predictions(request):
    df_tele = pd.DataFrame(list(Tele.objects.all().values()))
    df_jury = pd.DataFrame(list(JuRy.objects.all().values()))
    df_features = pd.DataFrame(list(Features.objects.all().values()))

    
    iso_eu = df_features['code']
    
    iso_dict = [{'iso': u}
        for u in iso_eu]

    output_iso = json.dumps(iso_dict)

    tele_dict = [{'from': row['from_country'], 'to': row['to_country']}
    for  index, row in df_tele.iterrows()]

    jury_dict = [{'from': row['from_country'], 'to': row['to_country']}
    for  index, row in df_jury.iterrows()]


    url = "https://drive.google.com/file/d/1oJxlSRVp11C-M9vyBraGuuyHxlpQWVgT/view?usp=sharing"
    countries  = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]
    
    response = urllib.request.urlopen(countries)
    
    input_dict = json.loads(response.read())
    output_json = json.dumps(input_dict)


    return render(request,'predictions.html', {"json_map": output_json, "country_codes": output_iso, "tele": tele_dict, "jury": jury_dict})
    

# GO COUNTRY VIEW
def go_country(request, _code):
    df_average = pd.DataFrame(list(MeanScoresByYear.objects.all().values()))
    df_average = df_average.groupby(['to_country', 'year']).agg({'points': ['mean']})

    x = df_average.loc[[_code]].index.get_level_values('year')
    y = df_average.loc[[_code]][('points', 'mean')]
    z = np.poly1d(np.polyfit(x, y, 1))(x)

    mpl_fig1  = plt.figure(figsize=(16,6))
    mpl_fig1.tight_layout()
    plt.plot(x, y, color='green', linestyle='dashed', linewidth = 3, marker='o', markerfacecolor='blue', markersize=12)
    plt.plot(x, z,"r--", linewidth = 3)

    for year, average_points in zip(x, y): 
        plt.text(year, average_points+0.2, str(round(average_points, 2)))
        

    country = ISO.objects.get(code = _code).name
    plt.xlabel('Years')
    plt.ylabel('Average Points')

    flike = io.BytesIO()
    mpl_fig1.savefig(flike)
    b64_fig1 = base64.b64encode(flike.getvalue()).decode()
    

    df_mean = pd.DataFrame(list(MeanScores.objects.all().values()))
    df_features = pd.DataFrame(list(Features.objects.all().values()))

    names = df_mean["id"]
    
    for index, row in df_mean.iterrows():
        names[index] = df_features.loc[df_features['code'] == row['to_country']]['name'].values[0] 
        if(names[index]) == "Russian Federation": names[index] = "Russia"
        elif(names[index]) == "Macedonia, the Former Yugoslav Republic of": names[index] = "Macedonia"
        elif(names[index]) == "Moldova, Republic of": names[index] = "Moldova"

    df_mean['name'] = names.values


    # average points given by a specifc country to each country
    df = df_mean
    df = df_mean.groupby(['from_country', 'to_country','name']).mean().reset_index()
    df = df[df['from_country']== _code].sort_values(by=['points'])
    length = int(len(df)/2)
    df1 = df.iloc[:length,:]
    df2 = df.iloc[length:,:]

    #figsize=(16,10)
    mpl_fig2, axs = plt.subplots(2,figsize=(16,6))
    mpl_fig2.subplots_adjust( hspace=0.5)
    
    x1=df1['name']
    y1=df1['points']
    axs[0].title.set_text("Lower half")
    axs[1].title.set_text("Uper half")
    axs[0].plot(x1, y1, 'bo', rasterized= True)
    axs[1].plot(df2['name'], df2['points'], 'bo', rasterized= True)



    axs[0].tick_params(labelrotation=45)
    axs[1].tick_params(labelrotation=45)

    flike = io.BytesIO()
    mpl_fig2.savefig(flike)
    b64_fig2 = base64.b64encode(flike.getvalue()).decode()

    # average points given by a specifc country to each country
    df_mean = pd.DataFrame(list(MeanScores.objects.all().values()))

    names = df_mean["id"]
    for index, row in df_mean.iterrows():
        names[index] = df_features.loc[df_features['code'] == row['from_country']]['name'].values[0] 
        if(names[index]) == "Russian Federation": names[index] = "Russia"
        elif(names[index]) == "Macedonia, the Former Yugoslav Republic of": names[index] = "Macedonia"
        elif(names[index]) == "Moldova, Republic of": names[index] = "Moldova"
    df_mean['name'] = names.values

    df = df_mean.groupby(['to_country', 'from_country','name']).mean().reset_index()
    df = df[df['to_country']== _code].sort_values(by=['points'])
    length = int(len(df)/2)
    df1 = df.iloc[:length,:]
    df2 = df.iloc[length:,:]

    #figsize=(16,10)
    mpl_fig3, axs = plt.subplots(2,figsize=(16,6))
    mpl_fig3.subplots_adjust( hspace=0.5)
    x1=df1['name']
    y1=df1['points']
    axs[0].title.set_text("Lower half")
    axs[1].title.set_text("Upper half")
    axs[0].plot(x1, y1, 'bo', rasterized= True)
    axs[1].plot(df2['name'], df2['points'], 'bo', rasterized= True)

    axs[0].tick_params(labelrotation=45)
    axs[1].tick_params(labelrotation=45)

    flike = io.BytesIO()
    mpl_fig3.savefig(flike)
    b64_fig3 = base64.b64encode(flike.getvalue()).decode()
    

    return render(request,'country.html', {'plot_div1' : b64_fig1,'plot_div2' : b64_fig2,'plot_div3' : b64_fig3, 'country' : country})
    

## NETWORK GRAPH VIEW   
def go_graph(request):
    df_features =  pd.DataFrame(list(Features.objects.all().values()))
    nodes  = df_features.loc[:, df_features.columns != 'country_border_code']
    edges = pd.DataFrame()
    From = []
    To = []
    pos = []
    df_features['pos'] = ""

    country_codes = np.array(
                        [['GR', 'ME', 'MK', 'RS'],
                        ['FR', 'ES'],
                        ['AZ', 'GE', 'IR', 'TR'],
                        ['nan'],
                        ['CZ', 'DE', 'HU', 'IT', 'LI', 'SK', 'SI', 'CH'],
                        ['AM', 'GE', 'IR', 'RU', 'TR'],
                        ['LV', 'LT', 'PL', 'RU', 'UA'],
                        ['FR', 'DE', 'LU', 'NL'],
                        ['HR', 'ME', 'RS'],
                        ['GR', 'MK', 'RO', 'RS', 'TR'],
                        ['BA', 'HU', 'ME', 'RS', 'SI'],
                        ['nan'],
                        ['AT', 'DE', 'PL', 'SK'],
                        ['DE'],
                        ['LV', 'RU'],
                        ['NO', 'RU', 'SE'],
                        ['AD', 'BE', 'DE', 'IT', 'LU', 'MC', 'ES', 'CH'],
                        ['AM', 'AZ', 'RU', 'TR'],
                        ['AT', 'BE', 'CZ', 'DK', 'FR', 'LU', 'NL', 'PL', 'CH'],
                        ['AL', 'BG', 'MK', 'TR'],
                        ['AT', 'HR', 'RO', 'RS', 'SK', 'SI', 'UA'],
                        ['nan'],
                        ['GB'],
                        ['EG', 'JO', 'LB', 'PS', 'SY'],
                        ['AT', 'FR', 'SM', 'SI', 'CH', 'VA'],
                        ['BY', 'EE', 'LT', 'RU'],
                        ['BY', 'LV', 'PL', 'RU'],
                        ['BE', 'DE', 'FR'],
                        ['AL', 'BG', 'GR', 'RS'],
                        ['nan'],
                        ['RO', 'UA'],
                        ['FR'],
                        ['AL', 'BA', 'HR', 'RS'],
                        ['DZ', 'ES', 'EH'],
                        ['BE', 'DE'],
                        ['FI', 'RU', 'SE'],
                        ['BY', 'CZ', 'DE', 'LT', 'RU', 'SK', 'UA'],
                        ['ES'],
                        ['BG', 'HU', 'MD', 'RS', 'UA'],
                        ['AZ', 'BY', 'CN', 'EE', 'FI', 'GE', 'KZ', 'KP', 'LV', 'LT', 'MN', 'NO', 'PL', 'UA'],
                        ['IT'],
                        ['AL', 'BA', 'BG', 'HR', 'HU', 'ME', 'MK', 'RO'],
                        ['AT', 'CZ', 'HU', 'PL', 'UA'],
                        ['AT', 'HR', 'HU', 'IT'],
                        ['AD', 'FR', 'GI', 'MA', 'PT'],
                        ['FI', 'NO'],
                        ['AT', 'FR', 'DE', 'IT', 'LI'],
                        ['AM', 'AZ', 'BG', 'GE', 'GR', 'IR', 'IQ', 'SY'],
                        ['BY', 'HU', 'MD', 'PL', 'RO', 'RU', 'SK'],
                        ['IE']])

    df_features['country_border_code'] = country_codes
    for index, row in df_features.iterrows():
    #create position from lat and lon
        row['pos'] = [float(row['lat']),float(row['lon'])]       
        #extract all country edges

        for i in range(len(row['country_border_code'])):

            _from = row['code']
            _to = row['country_border_code'][i]           
            #remove edges to countries outside the graph  
            if(_to in df_features['code'].tolist()):
                From.append(_from)
                To.append(_to)
    edges['to'] = To
    edges['from'] = From
    pos = df_features['pos'].to_dict()
    nodes["pos"] = pos

    #create networkx nodes
    G = nx.from_pandas_edgelist(edges,'from','to') #networkx does not add duplicate edges

    #create nodes for D3 and copy proprties from features dataframe
    nodes2 = [{
        'id': i,'name':df_features.loc[df_features['code'] == i]['name'].values[0], 
        'continent':df_features.loc[df_features['code'] == i]['continent'].values[0],
        'lat':df_features.loc[df_features['code'] == i]['lat'].values[0],
        'lon':df_features.loc[df_features['code'] == i]['lon'].values[0]}
         for i in G.nodes()]
  
    
    #create links for D3
    edges = [{'from': u[0], 'to': u[1]}
            for u in G.edges()]

    #write graph to json
    data = json.dumps({'nodes': nodes2, 'edges': edges},indent=4,)
    
    url = "https://drive.google.com/file/d/1Kc4xTx2cWS0vnLoWzL_sG_Wm7AFZufFh/view?usp=sharing"
    countries  = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]
    response = urllib.request.urlopen(countries)
    
    input_dict = json.loads(response.read())

    output_json = json.dumps(input_dict)

    

    iso_eu = df_features['code']
    
    iso_dict = [{'iso': u}
        for u in iso_eu]

    output_iso = json.dumps(iso_dict)


    return render(request,'graph.html', {"json_data": data, "json_map": output_json, "country_codes": output_iso} )
