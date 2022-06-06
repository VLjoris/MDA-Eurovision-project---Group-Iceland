from django.apps import AppConfig

class MyAppconfig(AppConfig):
    name = 'MDAsetup'
    verbose_name = 'MDAsetup_'
    def ready(self):


        ### esc =  eurovision song contest
        #https://www.kaggle.com/datasets/datagraver/eurovision-song-contest-scores-19752019?resource=download
        esc_1975_2019 =  "eurovision_song_contest_1975_2019.xlsx"

        #created by us
        esc_additional = "Eurovision additional.xlsx"

        #http://www.cepii.fr/cepii
        geo_cepii = "geo_cepii.xls"

        #https://github.com/geodatasource/country-borders/blob/master/GEODATASOURCE-COUNTRY-BORDERS.CSV
        geo_borders = "GEODATASOURCE-COUNTRY-BORDERS.csv"

        #https://datahub.io/core/country-list#resource-data
        iso2 = "iso2.csv"

        #https://timezonedb.com/download
        time_zone = "time_zone.csv"

        #load data in pandas df
        df_iso2_convert = pd.read_csv("data/" + iso2)
        df_borders = pd.read_csv("data/" + geo_borders)
        df_geo = pd.read_excel("data/" + geo_cepii,header=0)
        df_additional = pd.read_excel("data/" + esc_additional, header=0)
        df_esc = pd.read_excel("data/" + esc_1975_2019,sheet_name = "Data",header=0)

        headers = ["zone_name","country_code","abbreviation","time_start","gmt_offset","dst"]
        df_timezone = pd.read_csv('data/' +  time_zone,names=headers)

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