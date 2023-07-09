import pandas as pd


# data filepaths
inc_data_fp = 'data/animal-rescue-info-wmids.xlsx'
paw_data_fp = 'data/PAW.csv'
bhm_2021_fp = 'data/2021_Census_Profile___Wards_AF.xlsx'
census_2021_fp = 'data/census_2021.csv'

# census population growths
census_pop_growths = {
    'Birmingham': 6.7,
    'Walsall': 5.5,
    'Solihull': 4.6,
    'Coventry': 8.9,
    'Dudley': 3.4,
    'Sandwell': 11,
    'Wolverhampton': 5.7
}

# corona dates:
# 2020
# 26 March: First lockdown announced
# 10 May: Lockdown eased
# 1 June: First pupils return to school
# 15 JUne: Non-essential shops reopen
# 4 July: Pubs, salons and shops repoen
# 14 September: 'Rule of six'
# 14 October: Regional tier system introduced
# 5 November: ‘Circuit-breaker’ national lockdown begins
# 2 December: Another tier system
# 26 December: Most of the country moved to tier four
# 2021
# 6 January: Third national lockdown begins
# 15 February: Hotel quarantine introduced
# 8 March: Schools reopen
# 29 March outdoor gatherings allowed
# 12 April: businesses reopen
# 17 May: up to 30 meeting
# 19 July: Most remaining restrictions lifted
# https://www.instituteforgovernment.org.uk/sites/default/files/2022-12/timeline-coronavirus-lockdown-december-2021.pdf

corona_periods = {
    "First lockdown": [pd.Timestamp(year=2020, month=3, day=26), pd.Timestamp(year=2020, month=5, day=9)],
    "Step-wise loosening of restrictions": [pd.Timestamp(year=2020, month=5, day=10), pd.Timestamp(year=2020, month=10, day=13)],
    "Regional tier system introduced": [pd.Timestamp(year=2020, month=10, day=14), pd.Timestamp(year=2020, month=11, day=4)],
    "Second lockdown": [pd.Timestamp(year=2020, month=11, day=5), pd.Timestamp(year=2020, month=12, day=1)],
    "New tier system introduced": [pd.Timestamp(year=2020, month=12, day=2), pd.Timestamp(year=2021, month=1, day=5)],
    "Third lockdown": [pd.Timestamp(year=2021, month=1, day=6), pd.Timestamp(year=2021, month=3, day=7)],
    "Step-wise loosening of restrictions": [pd.Timestamp(year=2021, month=3, day=8), pd.Timestamp(year=2021, month=7, day=18)]
}

# animal keyword lookup
animal_keywords = {
    'dog': [
        'dog', 'greyhound', 'jack russell', 'puppy', 'huskey',
        'german shepherd', 'terrier', 'chihuahua', 'jack russel',
        'puppies', 'labrador'
    ],
    'cat': ['cat', 'kitten', ' k itten '],
    'bird': [
        'bird', 'pigeon', 'pidgeon', 'swift', 'falcon', 'crow', 'magpie',
        'kestrel', 'eagle', 'gull', 'heron', 'swan', 'goose', 'parrot',
        'sparrow', 'owl', 'starling', 'hawk', 'duck', 'duckling', 'budgie',
        'geese', 'mallard', 'duickling', 'kesterl', 'chick', 'swirft',
        'cygnet', 'gosling'
    ],
    'horse': ['horse', 'foal', 'pony', 'dorse '],
    'cow': ['cow', 'calf'],
    'pig': ['pig'],
    'sheep': ['sheep', 'ewe', 'lamb'],
    'deer': ['deer', ' dear '],
    'fox': ['fox', 'fos '],
    'squirrel': ['squirrel'],
    'snake': ['snake', 'boa'],
    'small animal': [
        'hamster', 'guinea pig', 'rabbit', 'hedgehog', 'chinchilla', 'badger'
    ]
}

# toggle for KML download
download_kml = False

# doogal district ID ranges
dist_ranges ={
    'Birmingham': [5011118, 5011186],
    'Coventry': [5001218, 5001235],
    'Dudley': [5001236, 5001259],
    'Sandwell': [5001260, 5001283],
    'Solihull': [5001284, 5001300],
    'Walsall': [5001301, 5001320],
    'Wolverhampton': [5014838, 5014857]
}