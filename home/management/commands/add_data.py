from ast import Index
from cgitb import handler
from django.core.management.base import BaseCommand
import pandas as pd
import urllib.request as urllibd
from py2neo import Graph,Node,Relationship
import datetime, pytz
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from sqlalchemy import create_engine, true
from home.models import *
import xlrd
import openpyxl


class Command(BaseCommand):
    help = " A command to add data from excel files to DB"

    def handle(self, *args,**options):
        print("Preparing data..")

        ### esc =  eurovision song contest
        #https://www.kaggle.com/datasets/datagraver/eurovision-song-contest-scores-19752019?resource=download
        url = 'https://docs.google.com/spreadsheets/d/1I4NCz3jToATZkhqVC934zcuRobeod42c/edit?usp=sharing&ouid=106547722922036463870&rtpof=true&sd=true'
        esc_1975_2019 =  'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]

        #created by us
        url = 'https://docs.google.com/spreadsheets/d/1gNxCahXd5SBHFsLnaYGkFsD90G9SPDAu/edit?usp=sharing&ouid=106547722922036463870&rtpof=true&sd=true'
        esc_additional = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]

        #http://www.cepii.fr/cepii
        url = 'https://docs.google.com/spreadsheets/d/1A5rEV4ulp1Jrnki5kd9ygulOXc2cW6FK/edit?usp=sharing&ouid=106547722922036463870&rtpof=true&sd=true'
        geo_cepii = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]

        #https://github.com/geodatasource/country-borders/blob/master/GEODATASOURCE-COUNTRY-BORDERS.CSV
        url = 'https://drive.google.com/file/d/19cdzS1Yo0vXj3H0b48wCgaitzsegwdkC/view?usp=sharing'
        geo_borders = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]

        #https://datahub.io/core/country-list#resource-data
        url = 'https://drive.google.com/file/d/10oOapt2UxsOaUUlxjGwbJ1gmTqIv_Bei/view?usp=sharing'
        iso2 = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]

        #https://timezonedb.com/download
        url = 'https://drive.google.com/file/d/1k5D7EiQOFltF3BKsMmlrkJjwIO4Ik6FC/view?usp=sharing'
        time_zone = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]


        #predictions for 2023
        url = 'https://drive.google.com/file/d/1TSy_Tv5PHQ5vlZ3GvgXrKvBcIfm9wlPx/view?usp=sharing'
        tele2023 = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]

        url = 'https://drive.google.com/file/d/18vfn3GdKY3VaubN-DrTjFq7p3SlPT6J9/view?usp=sharing'
        jury2023 = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]

        #load data in pandas df
        
        df_iso2_convert = pd.read_csv(iso2)
        df_borders = pd.read_csv(geo_borders)
        df_geo = pd.read_excel(geo_cepii,header=0)
        df_additional = pd.read_excel( esc_additional, header=0)
        df_esc = pd.read_excel(esc_1975_2019,sheet_name = "Data",header=0)

        headers = ["zone_name","country_code","abbreviation","time_start","gmt_offset","dst"]
        df_timezone = pd.read_csv(time_zone,names=headers)

        headers = ["from_country_full","to_country_full","jury_or_voting","year","voted", "from_country", "to_country"]
        df_tele = pd.read_csv(tele2023,names=headers)
        df_jury = pd.read_csv(jury2023,names=headers)

        df_tele.drop(['from_country_full', 'to_country_full'], axis = 1)
        df_jury.drop(['from_country_full', 'to_country_full'], axis = 1)

      

        df_features = []
        faulty_countries = []
        df_country_lookup = []
        # converts country columm to an iso2 column. Provided a lookup table containing the correct spelling of wrongly spelled countries.
        # run with empty lookup_table to get wronly spelled countries and update lookup_table aferwards 
        def country_to_iso2(df, columns = [] , lookup_table = []): 
            global faulty_countries
            global df_country_lookup
            faulty_countries = []
            for column in columns:
                df[column].apply(get_faulty_countries)
                try: 
                    df_country_lookup = pd.DataFrame({'faulty': faulty_countries, 'correct': lookup_table})
                except:
                    print("lookup table does not size of faulty_countries table : \n" + "lookup: " + str(lookup_table) + "\n faulty: " + str(faulty_countries) )
                    break
                newname = column + '_iso2'
                df[newname] = df[column].apply(get_iso2)
                
        # dds a new country name to an array with wrongly spelled countries
        def get_faulty_countries(country):
            global faulty_countries
            code = df_iso2_convert.loc[df_iso2_convert['Name'] == country]["Code"].values
            if code.size == 0:
                if country not in faulty_countries:
                    faulty_countries.append(country)

        # matches a worngly spelled country to the correct format
        def fix_country(country):
            global df_country_lookup
            new_country = df_country_lookup.loc[df_country_lookup["faulty"] == country]["correct"].values 
            if new_country.size > 0:
                return new_country[0]
            else: 
                return "Nan"

        # finds the iso2 code for a country name
        def get_iso2(country):
            code = df_iso2_convert.loc[df_iso2_convert['Name'] == country]["Code"].values
            if code.size > 0:
                return code[0]
            else:
                return df_iso2_convert.loc[df_iso2_convert['Name'] == fix_country(country)]["Code"].values[0]

        # copies features from a dataframe (with an iso2 column) into df_features
        def copy_features(df,iso2_column, features = []):    
            for feature in features:
                df_features[feature] = ""
                for index, row in df_features.iterrows():
                    val = df.loc[df[iso2_column]== index][feature].values
                    if val.size > 0:
                        df_features.loc[index,feature] = val[0]
                    else:
                        row[feature] = "Nan"

                        
        def get_utc_offset(zone):
            return datetime.datetime.now(pytz.timezone(zone)).strftime('%z')
        #Rename countries
        df_esc['From country'] = df_esc['From country'].replace(['Macedonia'],'F.Y.R. Macedonia')
        df_esc['To country'] = df_esc['To country'].replace(['Macedonia'],'F.Y.R. Macedonia')

        df_esc['From country'] = df_esc['From country'].replace(['The Netherands'],'The Netherlands')
        df_esc['To country'] = df_esc['To country'].replace(['The Netherands'],'The Netherlands')

        # drop uninteresting columns
        df_esc = df_esc.drop(["Duplicate"], axis =1)

        # Renaming the Points column to exclude the spaces
        df_esc.rename(columns={'Points      ':'Points'}, inplace=True)

        ## create iso2 column from the country columns
        lookup = ['Netherlands','Macedonia, the Former Yugoslav Republic of', 'Bosnia and Herzegovina', 'Russian Federation', 'Macedonia, the Former Yugoslav Republic of','Serbia','Moldova, Republic of', 'Macedonia, the Former Yugoslav Republic of']
        country_to_iso2(df_esc, ['From country', 'To country'], lookup ) 
                
        lookup = ['Macedonia, the Former Yugoslav Republic of', 'Moldova, Republic of', 'Russian Federation']
        country_to_iso2(df_additional, ["Unnamed: 0"], lookup)

        ### create a lookup table for iso2
        iso2_list = []
        for index, row in df_esc.iterrows():   
            iso2 = row["From country_iso2"]
            if iso2 not in iso2_list:
                iso2_list.append(iso2)
        df_iso2 = df_iso2_convert[df_iso2_convert['Code'].isin(iso2_list)].set_index('Code')
        df_features = df_iso2.copy() #copy iso2 and country names into feature matrix

        # copy interesting country features ino feature matrix based on matching iso2
        geo_features = ['continent', 'langoff_1','lat','lon','colonizer1'] #features that seem interesting? 
        copy_features(df_geo,"iso2", geo_features)

        additional_features = ['Religion', 'Most Common Country of Origin of Immigrants'] 
        copy_features(df_additional,"Unnamed: 0_iso2",additional_features)

        #concatenate border ios2 codes into list and ad border iso2 codes to feature matrix
        df_borders = pd.DataFrame(df_borders.groupby("country_code")["country_border_code"].apply(list)).reset_index(level=0)
        feature = ["country_border_code"]
        copy_features(df_borders, "country_code",feature)

        #convert df_timezone to iso2|timezone format and calculate UTC_offset from timezone
        df_timezone = df_timezone.groupby("country_code")["zone_name"].first().reset_index(level=0)
        df_timezone['UTC_offset'] = df_timezone['zone_name'].apply(get_utc_offset) 
        feature = ['UTC_offset']
        copy_features(df_timezone,'country_code',feature)

        # Deleting rows where From country is the same as To country
        df_esc = df_esc[df_esc['From country'] != df_esc['To country']]

        #rename columns 
        df_features.rename(columns = {'Most Common Country of Origin of Immigrants': 'Immigrants'},inplace = True)
        #update missing data
        df_features.at['MC', 'continent'] = 'Europe'
        df_features.at['MC', 'langoff_1'] = 'French'
        df_features.at['MC', 'lat'] = 43.7384
        df_features.at['MC', 'lon'] = 7.4246
        df_features.at['MC', 'colonizer1'] = 'FRA'

        df_features.at['ME', 'continent'] = 'Europe'
        df_features.at['ME', 'langoff_1'] = 'Montenegrin'
        df_features.at['ME', 'lat'] = 42.7087
        df_features.at['ME', 'lon'] = 19.3744
        df_features.at['ME', 'colonizer1'] = 'TUR'

        df_features.at['RS', 'continent'] = 'Europe'
        df_features.at['RS', 'langoff_1'] = 'Serbo-Croatian'
        df_features.at['RS', 'lat'] = 44.0165
        df_features.at['RS', 'lon'] = 21.0059
        df_features.at['RS', 'colonizer1'] = 'TUR'

        df_features.at['AD', 'Religion'] = 'Catholic'
        df_features.at['AD', 'Most Common Country of Origin of Immigrants'] = 'Spain'

        df_features.at['BA', 'Religion'] = 'Islam'
        df_features.at['BA', 'Most Common Country of Origin of Immigrants'] = 'Syria'

        df_features.at['LU', 'Religion'] = 'Catholic'
        df_features.at['LU', 'Most Common Country of Origin of Immigrants'] = 'France'

        df_features.at['MC', 'Most Common Country of Origin of Immigrants'] = 'France'
        df_features.at['MC', 'Religion'] = 'Catholic'

        df_features.at['SK', 'Most Common Country of Origin of Immigrants'] = 'Ukraine'
        df_features.at['SK', 'Religion'] = 'Catholic'

        # Adding NaN's into features
        
        df_iso2['id'] = range(1, len(df_iso2) + 1)

        df_tele['id'] = range(1, len(df_tele) + 1)
        df_jury['id'] = range(1, len(df_jury) + 1)


        df_features['country_border_code'] = df_features['country_border_code'].astype(str) #len = 50
        df_features['id'] = range(1, len(df_features) + 1)

       
        df_mean_from_to = df_esc.groupby(['From country_iso2', 'To country_iso2']).mean().reset_index().drop(['Year'],axis = 1)  #len = 2500
        df_mean_from_to['id'] = range(1, len(df_mean_from_to) + 1)
        
        df_average_points_per_country_by_year = df_esc.groupby(['To country_iso2', 'Year']).mean().reset_index() # len = 1280
        df_average_points_per_country_by_year['id'] = range(1, len(df_average_points_per_country_by_year) + 1)


        engine = create_engine('postgresql://dfhvwwqtmgsjfr:037abd163165f1ecdd9ef19b6ecbcba2864561ef036b251382e925cee3ebfc34@ec2-52-3-2-245.compute-1.amazonaws.com:5432/d3qoeutjojuhnm')

        df_features.to_sql(Features._meta.db_table,if_exists='replace', con=engine)
        df_mean_from_to.to_sql(MeanScores._meta.db_table,if_exists='replace', con=engine)
        df_average_points_per_country_by_year.to_sql(MeanScoresByYear._meta.db_table,if_exists='replace', con=engine)
        df_iso2.to_sql(ISO._meta.db_table,if_exists='replace', con=engine)
        df_tele.to_sql(Tele._meta.db_table,if_exists='replace', con=engine)
        df_jury.to_sql(JuRy._meta.db_table,if_exists='replace', con=engine)