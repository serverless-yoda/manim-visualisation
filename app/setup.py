# setup.py

import wbgapi as wb
import pandas as pd
import requests
import os

def setup_channel_assets():
    # 1. Fetch GDP Data (World Bank API)
    countries = [
    'USA', 'CHN', 'JPN', 'DEU', 'IND', 'GBR', 'FRA', 'BRA', 'ITA', 'CAN',
    'RUS', 'AUS', 'KOR', 'ESP', 'MEX', 'NLD', 'SAU', 'TUR', 'IDN', 'ARG',
    'ZAF', 'SWE', 'NOR', 'POL', 'BEL', 'CHE', 'AUT', 'DNK', 'FIN', 'IRN',
    'PAK', 'EGY', 'VNM', 'THA', 'PHL', 'MYS', 'SGP', 'ISR', 'UKR', 'GRC',
    'PRT', 'IRL', 'NZL', 'CHL', 'COL', 'PER', 'VEN', 'ECU', 'URY', 'PRY',
    'BOL', 'CUB', 'DOM', 'GTM', 'HND', 'SLV', 'NIC', 'PAN', 'CRI', 'JAM',
    'TTO', 'HTI', 'BLZ', 'BHS', 'BRB', 'GRD', 'ATG', 'DMA', 'LCA', 'VCT',
    'KWT', 'QAT', 'ARE', 'OMN', 'BHR', 'JOR', 'LBN', 'SYR', 'IRQ', 'YEM',
    'KAZ', 'UZB', 'TKM', 'KGZ', 'TJK', 'ARM', 'AZE', 'GEO', 'BLR', 'MDA',
    'UKR', 'LTU', 'LVA', 'EST', 'CZE', 'SVK', 'HUN', 'ROU', 'BGR', 'HRV',
    'SVN', 'BIH', 'SRB', 'MNE', 'MKD', 'ALB', 'KSV', 'CYP', 'MLT', 'LUX',
    'MON', 'SMR', 'AND', 'LIE', 'VAT', 'MLI', 'NGA', 'ETH', 'KEN', 'GHA',
    'CIV', 'CMR', 'TZA', 'UGA', 'ZWE', 'ZMB', 'AGO', 'NAM', 'BWA', 'LSO',
    'SWZ', 'MOZ', 'MDG', 'MWI', 'RWA', 'BDI', 'TGO', 'BEN', 'NER', 'MLI',
    'BFA', 'GIN', 'GNB', 'SLE', 'LBR', 'CIV', 'GHA', 'NGA', 'CMR', 'GAB',
    'COG', 'COD', 'CAF', 'TCD', 'SDN', 'SSD', 'ERI', 'DJI', 'SOM', 'TON',
    'FJI', 'PNG', 'WSM', 'SLB', 'VUT', 'KIR', 'TUV', 'FSM', 'MHL', 'PLW',
    'NRU', 'PNG', 'SLB', 'VAN', 'FJI', 'TON', 'SAM', 'KIR', 'TUV', 'FSM'
    ]
    countries = ['USA', 'CHN', 'RUS', 'JPN', 'DEU', 'IND', 'GBR', 'FRA', 'BRA', 'ITA', 'CAN', 'AUS', 'KOR', 'ISR', 'SAU']


    print("Fetching World Bank Data...")
    df = wb.data.DataFrame('NY.GDP.MKTP.CD', countries, time=range(2000, 2026))
    df = df.transpose()
    df.index = [int(i.replace('YR', '')) for i in df.index]
    df.to_csv('data/data.csv')

    # 2. Fetch Flags automatically
    # if not os.path.exists('images'): os.makedirs('images')
    # print("Downloading Flag Icons...")
    # for code in countries:
    #     url = f"https://flagcdn.com/w320/{code[:2].lower()}.png"

    #     img_data = requests.get(url).content
    #     with open(f"images/{code}.png", 'wb') as f:
    #         f.write(img_data)
    print("Setup Complete.")

if __name__ == "__main__":
    setup_channel_assets()