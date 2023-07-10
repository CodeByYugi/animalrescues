import glob
import holidays
import pandas as pd
from urllib.request import urlopen
import xml.etree.ElementTree as ET
from pathlib import Path
import geopandas as gpd
import prophet
from prophet.plot import plot_plotly, plot_components_plotly
from nltk import ngrams
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


def add_time_dimensions(to_prep, date_col='Incdate'):
    '''Function that converts datetime to financial year, week, month and checks for holidays'''
    # add helper columns for various date dimensions
    to_prep.loc[:, 'fin_year'] = to_prep[date_col].dt.to_period('Q-MAR').dt.qyear - 1
    to_prep.loc[:, 'month'] = to_prep[date_col].dt.to_period('M').dt.start_time
    to_prep.loc[:, 'week'] = to_prep[date_col].dt.to_period('W').dt.start_time
    to_prep.loc[:, 'weekday'] = to_prep[date_col].dt.day_of_week

    # import holidays dats in England
    eng_hol = holidays.country_holidays(
        'GB', subdiv='ENG',
        years=range(to_prep[date_col].min().year, to_prep[date_col].max().year+1)
    )

    # add helper column to indicate if incident date was a holiday or weekend
    to_prep.loc[:, 'BH_or_WE'] = 'No'
    to_prep.loc[to_prep.weekday.isin([5,6]), 'BH_or_WE'] = 'Weekend'
    to_prep.loc[to_prep[date_col].dt.date.isin(eng_hol), 'BH_or_WE'] = 'Bank Holiday'

    return to_prep


def group_animals(to_prep, animal_kw_dict, desc_col='Incident Detail'):
    '''Function to group animal into supertypes based on keyword dict'''
    # parse animal keywords and group into animal supertypes
    for animal, keyword_list in animal_kw_dict.items():
        to_prep.loc[
            to_prep[desc_col].str.lower().str.contains('|'.join(keyword_list)),
            'animal'
        ] = animal
    
    return to_prep


def modify_wards(to_prep, ward_col='Ward'):
    '''Function to align ward names in to_prep to post-2018 ward names'''
    # rename wards
    to_prep.loc[:, ward_col] = to_prep.Ward.str.replace(' Ward', '').copy()
    to_prep.loc[to_prep.Ward.isin(["St. Peter's", "St Peter's"]), ward_col] = 'St Peters'
    to_prep.loc[to_prep.Ward == "St. Michael's", ward_col] = "St Michael's"
    to_prep.loc[to_prep.Ward == "St. Pauls", ward_col] = 'St Pauls'

    # messy, manual reallocation of old wards to new ones post 2018
    to_prep.loc[to_prep.Ward == 'Bushbury South and Low Hill', ward_col] = 'Bushbury South & Low Hill'
    to_prep.loc[to_prep.Ward == 'Bournville', ward_col] = 'Bournville & Cotteridge'
    to_prep.loc[to_prep.Ward == 'Spring Vale', ward_col] = 'Ettingshall South & Spring Vale'
    to_prep.loc[to_prep.Ward == 'Longbridge', ward_col] = 'Longbridge & West Heath'
    to_prep.loc[to_prep.Ward == 'Sparkbrook', ward_col] = 'Sparkbrook & Balsall Heath East'
    to_prep.loc[to_prep.Ward == 'Hodge Hill', ward_col] = 'Bromford & Hodge Hill'
    to_prep.loc[to_prep.Ward == 'Moseley and Kings Heath', ward_col] = 'Moseley'
    to_prep.loc[to_prep.Ward == 'Brandwood', ward_col] = "Brandwood & King's Heath"
    to_prep.loc[to_prep.Ward == 'Soho', ward_col] = "Soho & Jewellery Quarter"
    to_prep.loc[to_prep.Ward == 'Bilston East', ward_col] = "Bilston South"
    to_prep.loc[to_prep.Ward == 'Lozells and East Handsworth', ward_col] = 'Lozells'
    to_prep.loc[to_prep.Ward == 'Ettingshall', ward_col] = 'Ettingshall North'
    to_prep.loc[to_prep.Ward == 'Stechford and Yardley North', ward_col] = 'Yardley West & Stechford'
    to_prep.loc[to_prep.Ward == 'Washwood Heath', ward_col] = 'Bromford & Hodge Hill'
    to_prep.loc[to_prep.Ward == 'Sutton New Hall', ward_col] = 'Sutton Walmley & Minworth'
    to_prep.loc[to_prep.Ward == 'Springfield', ward_col] = 'Hall Green North'
    to_prep.loc[to_prep.Ward == 'Hall Green', ward_col] = 'Hall Green South'
    to_prep.loc[to_prep.Ward == 'Kings Norton', ward_col] = "King's Norton South"
    to_prep.loc[to_prep.Ward == 'Tyburn', ward_col] = "Erdington"
    to_prep.loc[to_prep.Ward.isin(['Weoley', 'Selly Oak']), ward_col] = "Weoley & Selly Oak"

    to_prep.loc[to_prep.Ward == 'Tipton Green', 'District'] = "Sandwell"

    return to_prep


def download_district_kml(doogal_dict):
    '''Function to download Postcode KML files from Doogal'''
    for district, (kml_start, kml_end) in doogal_dict.items():
        for id in range(kml_start, kml_end+1):
            print(id)
            kml = urlopen(f"https://www.doogal.co.uk/kml/wards/E0{id}.kml").read()
            dist_name = ET.fromstring(kml)[0][1][1].text
            filename = Path(f'kml/{dist_name}.kml')
            filename.write_bytes(kml)


def load_and_combine_kml(kml_dir='kml'):
    '''Function for loading and combining KML files in target directory'''
    kml = gpd.GeoDataFrame()
    for kml_file in glob.glob(f'{kml_dir}/*.kml'):
        kml = pd.concat([kml, gpd.read_file(kml_file)])
    
    return kml


def combine_maps_w_data(kml_data, inc_data, census_data):
    map_data = (
        kml_data
        .join(
            (
                inc_data
                .groupby(['fin_year', 'District', 'Ward']).size()
                .unstack('fin_year').fillna(0)
                .assign(Total_Incidents=lambda x: x.sum(axis=1))
                .reset_index(level=0)
            ),
            how='left',
            on='Ward'
        )
    )

    map_data.loc[:, 'Ward'] = map_data.Ward.str.replace("'", '')

    map_data.loc[
        map_data.Ward.str.contains('Ettingshall'), 'Ward'
    ] = 'Ettingshall'

    map_data = map_data.dissolve(by='Ward', aggfunc='sum', numeric_only=False).reset_index()

    map_data.loc[
        map_data.Ward.isin(['Castle Vale', 'Allens Cross']),
        'District'
    ] = 'Birmingham'

    map_data.loc[
        map_data.Ward == 'Ettingshall',
        'District'
    ] = 'Wolverhampton'

    map_data = (
        map_data
        .join(census_data, how='left', on='Ward')
        .fillna(0)
        .assign(inc_per_pop=lambda x: x[[2021, 2022]].sum(axis=1).div(x.Observation * 2).mul(10000))
        .rename(
            columns={
                'Total_Incidents': 'Total Incidents',
                'Observation': 'Population (Census 2021)',
                'inc_per_pop': 'Incidents per 10,000 (21/22 - 22/23)',
                2013: '2013',
                2014: '2014',
                2015: '2015',
                2016: '2016',
                2017: '2017',
                2018: '2018',
                2019: '2019',
                2020: '2020',
                2021: '2021',
                2022: '2022'
            }
        )
    )

    return map_data


def fit_and_predict(to_fit, p=30, f='d'):
    m = prophet.Prophet()
    m.add_country_holidays(country_name='GB')
    m.fit(to_fit)
    future = m.make_future_dataframe(periods=p, freq=f)
    forecast = m.predict(future)

    return plot_components_plotly(m, forecast, uncertainty=False)


def filter_stopwords(q):
    filtered_list = []
    for word in word_tokenize(q):
        if word.casefold() not in set(stopwords.words("english")):
            filtered_list.append(word)
    return filtered_list


def get_ngrams(s, n=2):
    return [gram for gram in ngrams(s, n)]


def ngram_counts(data, n=2, col='Incident Detail'):
    return pd.Series([x for t in data[col].apply(filter_stopwords).apply(get_ngrams, args=(n,)).values for x in t]).value_counts()
