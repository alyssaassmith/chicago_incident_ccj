import datetime
import pandas as pd
import numpy as np
import os
import geopandas as gpd


def inc_data_read(start_year = 2018, full_dataset = True, convert_cook_crs = True):
    
    """
    Pulling in City of Chicago Incident data; returns pandas dataframe of incidents.
    start_year: input starting year for requested data
    full_dataset: choose to pull in full dataset or small subset of data
    convert_cook_crs: choose to convert to local espg to match beat data or not 
    """

    

    if full_dataset == True:
        print("Pulling full dataset")
        limit = 20000000
    else:
        print("Small subset")
        limit = 200
    
    # initialize datatime object
    today = datetime.date.today()
    
    # getting current year
    current_yr = today.year
    # initialize a list
    inc_df_list = []
    
    # for each year between 2018 and current year, pull in incident data    
    for year in range(start_year, current_yr + 1):
        inc_data_yr = pd.read_csv(
            f'https://data.cityofchicago.org/resource/ijzp-q8t2.csv?$limit={limit}&$where=date%20between%20%27{year}-01-01T00:00:00%27%20and%20%27{year}-12-31T23:59:59%27', storage_options={'verify': False}
        )
        inc_df_list.append(inc_data_yr)
        
    # concat lists of data from each list (dataframe of yearly arrests)
    inc_df = pd.concat(inc_df_list, ignore_index=True)

    # creating a geopandas dataframe from dataframe
    geometry = gpd.points_from_xy(inc_df.longitude, inc_df.latitude, crs="EPSG:4326")
    inc_gdf = gpd.GeoDataFrame(
    inc_df, geometry=geometry 
     )     



    # converting the espg to correct area for cook for beats and incidents to work together 
    if convert_cook_crs == True: 
        inc_gdf = inc_gdf.to_crs(epsg=26916) 
        
  
        print(inc_gdf.crs)
        print(inc_gdf.shape)

        return inc_gdf




if __name__ == "__main__":

    
    # In[310]:


    df = inc_data_read(start_year = 2018, full_dataset = True, convert_cook_crs = True)


    # In[312]:


    df.head()


    # In[314]:


    df['date'] = df['date'].astype(str)


    # In[316]:


    df['inc_data_read'] = pd.to_datetime(df['date'], errors='coerce')


    # In[318]:


    df['date'] = pd.to_datetime(df['date'])


    # In[320]:


    print(df['date'].head())


    # In[322]:


    print(df['date'].dtype)


    # In[324]:


    print(df['date'].unique())


    # In[357]:


    df['year'].unique()


    # In[326]:


    df['MONTH'] = df['date'].dt.month
    df['DAY'] = df['date'].dt.day
    df['YEAR'] = df['date'].dt.year


    # In[363]:


    df.columns


    # In[328]:


    df = df[(df['inc_data_read'] >= '2018-01-01') & (df['inc_data_read'] <= '2024-12-31')]


    # In[330]:


    lookup_path = "data/cpd_offense_lookup.txt"
    lookup = pd.read_csv(lookup_path, sep=',')


    # In[332]:


    df = df.merge(lookup, left_on=['iucr'], right_on=['IUCR'], how='left')


    # In[334]:


    print(lookup.dtypes)


    # In[336]:


    df['Domestic'] = df['domestic'].astype(str)
    df['DomesticSort'] = np.where(df['domestic'] == 'true', 1,
                        np.where(df['domestic'] == 'false', 0, np.nan))
    df['Domestic'] = df['domestic'].map({'true': 'DV Incident', 'false': 'Non-DV Incident'})


    # In[338]:


    domestic_keywords = ['Domestic Battery', 'Aggravated Domestic Battery']
    df.loc[df['OffenseDescription'].isin(domestic_keywords), 'DomesticSort'] = 1
    df.loc[df['OffenseDescription'].isin(domestic_keywords), 'Domestic'] = 'DV Incident'


    # In[340]:


    df['Arrest'] = df['arrest'].astype(str)
    df['ArrestSort'] = df['arrest'].map({'true': 1, 'false': 0})
    df['Arrest'] = df['arrest'].map({'true': 'arrest', 'false': 'No arrest'})


    # In[342]:


    def assign_police_district(beat):
        if beat in [111,112,113,114,121,122,123,124,131,132,133]: return 1
        elif beat in [211,212,213,214,215,221,222,223,224,225,231,232,233,234,235]: return 2
        elif 311 <= beat <= 334: return 3
        elif 411 <= beat <= 434: return 4
        elif 511 <= beat <= 533: return 5
        elif 611 <= beat <= 634: return 6
        elif 711 <= beat <= 735: return 7
        elif 811 <= beat <= 835: return 8
        elif 911 <= beat <= 935: return 9
        elif 1011 <= beat <= 1034: return 10
        elif 1111 <= beat <= 1135: return 11
        elif 1211 <= beat <= 1235: return 12
        elif 1411 <= beat <= 1434: return 14
        elif 1511 <= beat <= 1533: return 15
        elif 1611 <= beat <= 1655: return 16
        elif 1711 <= beat <= 1733: return 17
        elif 1811 <= beat <= 1834: return 18
        elif 1911 <= beat <= 1935: return 19
        elif 2011 <= beat <= 2033: return 20
        elif 2211 <= beat <= 2234: return 22
        elif 2411 <= beat <= 2433: return 24
        elif 2511 <= beat <= 2535: return 25
        return np.nan


    # In[344]:


    df['PoliceDistrict'] = df['beat'].apply(lambda x: assign_police_district(int(x)) if pd.notnull(x) else np.nan)


    # In[346]:


    df['CaseSort'] = 1
    df['Case'] = 'All Incidents'


    # In[348]:


    output_csv = "incident.csv"


    # In[350]:


    drop_cols = [
        'id', 'case_number', 'date', 'block', 'primary_type', 'description', 'location_description', 'fbi_code',
        'x_coordinate', 'y_coordinate', 'updated_on', 'latitude', 'longitude', 'location', 'MONTH', 'DAY'
    ]
    df.drop(columns=drop_cols, inplace=True)


    # In[352]:


    df.to_csv(output_csv, index=False, encoding='utf-8')








