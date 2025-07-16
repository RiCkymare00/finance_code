import pandas as pd
import numpy as np
import copy
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
import json
import time
import random

#gpr origin: https://policyuncertainty.com/gpr.html

def portfolio_yearly_returns(which,months): # non ribilanciato!
    rendimenti = ( dati[which] / dati[which].shift(months) ).mean(axis=1)
    return ( rendimenti.mean(axis=0)**(12/months) -1 )  , rendimenti.std(axis=0), rendimenti.count().sum() 

def get_gpr_codes_for_etf(etf_name, gpr_data):
    """
    Associa automaticamente gli ETF ai codici GPR corrispondenti
    """
    etf_name = etf_name.upper().strip()
    
    # Dizionario delle associazioni ETF -> GPR codes
    etf_to_gpr = {
        # Paesi singoli
        'JAPAN': ['GPRC_JPN'],
        'JAPAN IMI': ['GPRC_JPN'],
        'CHINA': ['GPRC_CHN'],
        'INDIA': ['GPRC_IND'],
        'BRAZIL': ['GPRC_BRA'],
        'CANADA': ['GPRC_CAN'],
        'UNITED KINGDOM': ['GPRC_GBR'],
        'KOREA': ['GPRC_KOR'],
        'TAIWAN': ['GPRC_TWN'],
        'SWITZERLAND': ['GPRC_CHE'],
        'SAUDI ARABIA': ['GPRC_SAU'],
        'MEXICO': ['GPRC_MEX'],
        'GERMANY': ['GPRC_DEU'],
        'FRANCE': ['GPRC_FRA'],
        'ITALY': ['GPRC_ITA'],
        'SPAIN': ['GPRC_ESP'],
        'NETHERLANDS': ['GPRC_NLD'],
        'BELGIUM': ['GPRC_BEL'],
        'AUSTRALIA': ['GPRC_AUS'],
        'HONG KONG': ['GPRC_HKG'],
        'SINGAPORE': ['GPRC_SGP'] if 'GPRC_SGP' in gpr_data else [],
        'THAILAND': ['GPRC_THA'],
        'MALAYSIA': ['GPRC_MYS'],
        'INDONESIA': ['GPRC_IDN'],
        'PHILIPPINES': ['GPRC_PHL'],
        'VIETNAM': ['GPRC_VNM'],
        'TURKEY': ['GPRC_TUR'],
        'SOUTH AFRICA': ['GPRC_ZAF'],
        'RUSSIA': ['GPRC_RUS'],
        'POLAND': ['GPRC_POL'],
        'HUNGARY': ['GPRC_HUN'],
        'CZECH REPUBLIC': ['GPRC_CZE'] if 'GPRC_CZE' in gpr_data else [],
        'ISRAEL': ['GPRC_ISR'],
        'EGYPT': ['GPRC_EGY'],
        'CHILE': ['GPRC_CHL'],
        'COLOMBIA': ['GPRC_COL'],
        'PERU': ['GPRC_PER'],
        'ARGENTINA': ['GPRC_ARG'],
        'VENEZUELA': ['GPRC_VEN'],
        'NORWAY': ['GPRC_NOR'],
        'SWEDEN': ['GPRC_SWE'],
        'DENMARK': ['GPRC_DNK'],
        'FINLAND': ['GPRC_FIN'],
        'PORTUGAL': ['GPRC_PRT'],
        'TUNISIA': ['GPRC_TUN'],
        'UKRAINE': ['GPRC_UKR'],
        
        # Regioni
        'WORLD': list(gpr_data.keys()),
        'ACWI': list(gpr_data.keys()),
        'MSCI WORLD': list(gpr_data.keys()),
        
        'EUROPE': ['GPRC_DEU', 'GPRC_FRA', 'GPRC_ITA', 'GPRC_ESP', 'GPRC_NLD', 'GPRC_BEL', 
                   'GPRC_CHE', 'GPRC_GBR', 'GPRC_SWE', 'GPRC_NOR', 'GPRC_DNK', 'GPRC_FIN', 
                   'GPRC_PRT', 'GPRC_POL', 'GPRC_HUN'],
        
        'EMU': ['GPRC_DEU', 'GPRC_FRA', 'GPRC_ITA', 'GPRC_ESP', 'GPRC_NLD', 'GPRC_BEL', 
                'GPRC_FIN', 'GPRC_PRT'],
        
        'EUROPE ex UK': ['GPRC_DEU', 'GPRC_FRA', 'GPRC_ITA', 'GPRC_ESP', 'GPRC_NLD', 'GPRC_BEL', 
                         'GPRC_CHE', 'GPRC_SWE', 'GPRC_NOR', 'GPRC_DNK', 'GPRC_FIN', 'GPRC_PRT', 
                         'GPRC_POL', 'GPRC_HUN'],
        
        'NORDIC COUNTRIES': ['GPRC_SWE', 'GPRC_NOR', 'GPRC_DNK', 'GPRC_FIN'],
        
        'EM (EMERGING MARKETS)': ['GPRC_CHN', 'GPRC_IND', 'GPRC_BRA', 'GPRC_RUS', 'GPRC_KOR', 
                                  'GPRC_TWN', 'GPRC_SAU', 'GPRC_MEX', 'GPRC_THA', 'GPRC_MYS', 
                                  'GPRC_IDN', 'GPRC_PHL', 'GPRC_VNM', 'GPRC_TUR', 'GPRC_ZAF', 
                                  'GPRC_POL', 'GPRC_HUN', 'GPRC_EGY', 'GPRC_CHL', 'GPRC_COL', 
                                  'GPRC_PER', 'GPRC_ARG'],
        
        'EM (EMERGING MARKETS) ex CHINA': ['GPRC_IND', 'GPRC_BRA', 'GPRC_RUS', 'GPRC_KOR', 
                                           'GPRC_TWN', 'GPRC_SAU', 'GPRC_MEX', 'GPRC_THA', 
                                           'GPRC_MYS', 'GPRC_IDN', 'GPRC_PHL', 'GPRC_VNM', 
                                           'GPRC_TUR', 'GPRC_ZAF', 'GPRC_POL', 'GPRC_HUN', 
                                           'GPRC_EGY', 'GPRC_CHL', 'GPRC_COL', 'GPRC_PER', 
                                           'GPRC_ARG'],
        
        'EM ASIA': ['GPRC_CHN', 'GPRC_IND', 'GPRC_KOR', 'GPRC_TWN', 'GPRC_THA', 'GPRC_MYS', 
                    'GPRC_IDN', 'GPRC_PHL', 'GPRC_VNM'],
        
        'EM LATIN AMERICA': ['GPRC_BRA', 'GPRC_MEX', 'GPRC_CHL', 'GPRC_COL', 'GPRC_PER', 
                             'GPRC_ARG', 'GPRC_VEN'],
        
        'PACIFIC ex JAPAN': ['GPRC_AUS', 'GPRC_HKG', 'GPRC_KOR', 'GPRC_TWN', 'GPRC_THA', 
                             'GPRC_MYS', 'GPRC_IDN', 'GPRC_PHL', 'GPRC_VNM'],
        
        'AC FAR EAST ex JAPAN': ['GPRC_CHN', 'GPRC_HKG', 'GPRC_KOR', 'GPRC_TWN', 'GPRC_THA', 
                                 'GPRC_MYS', 'GPRC_IDN', 'GPRC_PHL', 'GPRC_VNM'],
        
        'AC ASIA ex JAPAN': ['GPRC_CHN', 'GPRC_IND', 'GPRC_HKG', 'GPRC_KOR', 'GPRC_TWN', 
                             'GPRC_THA', 'GPRC_MYS', 'GPRC_IDN', 'GPRC_PHL', 'GPRC_VNM'],
        
        'NORTH AMERICA': ['GPRC_USA', 'GPRC_CAN'],
        
        'WORLD ex USA': [code for code in gpr_data.keys() if code != 'GPRC_USA'],
        
        'WORLD ex EMU': [code for code in gpr_data.keys() if code not in ['GPRC_DEU', 'GPRC_FRA', 'GPRC_ITA', 'GPRC_ESP', 'GPRC_NLD', 'GPRC_BEL', 'GPRC_FIN', 'GPRC_PRT']],
        
        'WORLD ex EUROPE': [code for code in gpr_data.keys() if code not in ['GPRC_DEU', 'GPRC_FRA', 'GPRC_ITA', 'GPRC_ESP', 'GPRC_NLD', 'GPRC_BEL', 'GPRC_CHE', 'GPRC_GBR', 'GPRC_SWE', 'GPRC_NOR', 'GPRC_DNK', 'GPRC_FIN', 'GPRC_PRT', 'GPRC_POL', 'GPRC_HUN']],
        
        'USA': ['GPRC_USA'],
        'UNITED STATES': ['GPRC_USA'],
        
        # Small cap variants
        'EMU SMALL CAP': ['GPRC_DEU', 'GPRC_FRA', 'GPRC_ITA', 'GPRC_ESP', 'GPRC_NLD', 'GPRC_BEL', 
                          'GPRC_FIN', 'GPRC_PRT'],
        'UNITED KINGDOM SMALL CAP': ['GPRC_GBR'],
    }
    
    # Cerca corrispondenza esatta
    if etf_name in etf_to_gpr:
        return etf_to_gpr[etf_name]
    
    # Cerca corrispondenza parziale
    for key, codes in etf_to_gpr.items():
        if key in etf_name or etf_name in key:
            return codes
    
    # Se non trova corrispondenza, prova con parole chiave
    keywords = {
        'JAPAN': ['GPRC_JPN'],
        'CHINA': ['GPRC_CHN'],
        'INDIA': ['GPRC_IND'],
        'BRAZIL': ['GPRC_BRA'],
        'CANADA': ['GPRC_CAN'],
        'UK': ['GPRC_GBR'],
        'BRITAIN': ['GPRC_GBR'],
        'KOREA': ['GPRC_KOR'],
        'TAIWAN': ['GPRC_TWN'],
        'SWITZERLAND': ['GPRC_CHE'],
        'SAUDI': ['GPRC_SAU'],
        'MEXICO': ['GPRC_MEX'],
        'GERMANY': ['GPRC_DEU'],
        'FRANCE': ['GPRC_FRA'],
        'ITALY': ['GPRC_ITA'],
        'SPAIN': ['GPRC_ESP'],
        'NETHERLANDS': ['GPRC_NLD'],
        'BELGIUM': ['GPRC_BEL'],
        'AUSTRALIA': ['GPRC_AUS'],
        'HONG KONG': ['GPRC_HKG'],
        'SINGAPORE': ['GPRC_SGP'] if 'GPRC_SGP' in gpr_data else [],
        'THAILAND': ['GPRC_THA'],
        'MALAYSIA': ['GPRC_MYS'],
        'INDONESIA': ['GPRC_IDN'],
        'PHILIPPINES': ['GPRC_PHL'],
        'VIETNAM': ['GPRC_VNM'],
        'TURKEY': ['GPRC_TUR'],
        'SOUTH AFRICA': ['GPRC_ZAF'],
        'RUSSIA': ['GPRC_RUS'],
        'POLAND': ['GPRC_POL'],
        'HUNGARY': ['GPRC_HUN'],
        'ISRAEL': ['GPRC_ISR'],
        'EGYPT': ['GPRC_EGY'],
        'CHILE': ['GPRC_CHL'],
        'COLOMBIA': ['GPRC_COL'],
        'PERU': ['GPRC_PER'],
        'ARGENTINA': ['GPRC_ARG'],
        'VENEZUELA': ['GPRC_VEN'],
        'NORWAY': ['GPRC_NOR'],
        'SWEDEN': ['GPRC_SWE'],
        'DENMARK': ['GPRC_DNK'],
        'FINLAND': ['GPRC_FIN'],
        'PORTUGAL': ['GPRC_PRT'],
        'TUNISIA': ['GPRC_TUN'],
        'UKRAINE': ['GPRC_UKR'],
        'USA': ['GPRC_USA'],
        'UNITED STATES': ['GPRC_USA'],
        'WORLD': list(gpr_data.keys()),
        'GLOBAL': list(gpr_data.keys()),
        'EMERGING': ['GPRC_CHN', 'GPRC_IND', 'GPRC_BRA', 'GPRC_RUS', 'GPRC_KOR', 'GPRC_TWN', 
                     'GPRC_SAU', 'GPRC_MEX', 'GPRC_THA', 'GPRC_MYS', 'GPRC_IDN', 'GPRC_PHL', 
                     'GPRC_VNM', 'GPRC_TUR', 'GPRC_ZAF', 'GPRC_POL', 'GPRC_HUN', 'GPRC_EGY', 
                     'GPRC_CHL', 'GPRC_COL', 'GPRC_PER', 'GPRC_ARG'],
        'EUROPE': ['GPRC_DEU', 'GPRC_FRA', 'GPRC_ITA', 'GPRC_ESP', 'GPRC_NLD', 'GPRC_BEL', 
                   'GPRC_CHE', 'GPRC_GBR', 'GPRC_SWE', 'GPRC_NOR', 'GPRC_DNK', 'GPRC_FIN', 
                   'GPRC_PRT', 'GPRC_POL', 'GPRC_HUN'],
        'ASIA': ['GPRC_CHN', 'GPRC_JPN', 'GPRC_IND', 'GPRC_KOR', 'GPRC_TWN', 'GPRC_HKG', 
                 'GPRC_THA', 'GPRC_MYS', 'GPRC_IDN', 'GPRC_PHL', 'GPRC_VNM'],
        'PACIFIC': ['GPRC_AUS', 'GPRC_JPN', 'GPRC_HKG', 'GPRC_KOR', 'GPRC_TWN', 'GPRC_THA', 
                    'GPRC_MYS', 'GPRC_IDN', 'GPRC_PHL', 'GPRC_VNM'],
        'LATIN': ['GPRC_BRA', 'GPRC_MEX', 'GPRC_CHL', 'GPRC_COL', 'GPRC_PER', 'GPRC_ARG', 'GPRC_VEN'],
        'AMERICA': ['GPRC_USA', 'GPRC_CAN', 'GPRC_BRA', 'GPRC_MEX', 'GPRC_CHL', 'GPRC_COL', 
                    'GPRC_PER', 'GPRC_ARG', 'GPRC_VEN'],
        'NORDIC': ['GPRC_SWE', 'GPRC_NOR', 'GPRC_DNK', 'GPRC_FIN'],
        'EMU': ['GPRC_DEU', 'GPRC_FRA', 'GPRC_ITA', 'GPRC_ESP', 'GPRC_NLD', 'GPRC_BEL', 'GPRC_FIN', 'GPRC_PRT'],
    }
    
    for keyword, codes in keywords.items():
        if keyword in etf_name:
            return codes
    
    # Default: restituisce tutti i codici GPR (assume sia un indice mondiale)
    print(f"⚠️  Nessuna corrispondenza trovata per '{etf_name}', assumendo indice mondiale")
    return list(gpr_data.keys())

def calculate_gpr_sum(etf_list, gpr_data):
    """
    Calcola la somma totale del GPR per una lista di ETF
    """
    all_gpr_codes = set()
    
    for etf in etf_list:
        codes = get_gpr_codes_for_etf(etf, gpr_data)
        all_gpr_codes.update(codes)
    
    total_gpr = sum(float(gpr_data[code]) for code in all_gpr_codes if code in gpr_data)
    
    return total_gpr, list(all_gpr_codes)

pd.set_option('display.max_colwidth', None)
mesi = 60 #5 anni
eliminati2 = ["ACWI","USA","NORTH AMERICA","WORLD ex EMU", "WORLD ex EUROPE", "EM (EMERGING MARKETS)", "EM ASIA",
             "EM (EMERGING MARKETS) ex CHINA", "EM ASIA", "AC FAR EAST ex JAPAN", "AC ASIA ex JAPAN", "EMU", "WORLD ex USA",
             "EUROPE ex UK", "FRANCE", "JAPAN", "EM LATIN AMERICA", "EMU SMALL CAP", "AUSTRALIA", "UNITED KINGDOM SMALL CAP", "POLAND"]

urlo = "https://raw.githubusercontent.com/paolocole/Stock-Indexes-Historical-Data/main/DAILY/NET/EUR/"
elenco = pd.read_excel("https://www.paolocoletti.com/wp-content/uploads/youtube/etfs_with_msci.xlsx" , sheet_name="selezionati" , index_col=0)
elenco["url"] = urlo + elenco["Path"] + "/" + elenco["File"] + ".csv"
elenco["url"] = elenco["url"].str.replace("\\","/") 

# Dati GPR
gpr_data = {
    "GPRC_ARG":"0.0207929033786058","GPRC_AUS":"0.298031598329544","GPRC_BEL":"0.17327418923378","GPRC_BRA":"0.0831716135144234","GPRC_CAN":"0.977266430854797","GPRC_CHE":"0.0762406438589096","GPRC_CHL":"0.0138619355857372","GPRC_CHN":"1.29609096050262","GPRC_COL":"0.0207929033786058","GPRC_DEU":"0.831716120243073","GPRC_DNK":"0.0831716135144234","GPRC_EGY":"0.34654837846756","GPRC_ESP":"0.263376772403717","GPRC_FIN":"0.0554477423429489","GPRC_FRA":"1.02578318119049","GPRC_GBR":"2.55059599876404","GPRC_HKG":"0.0554477423429489","GPRC_HUN":"0.0554477423429489","GPRC_IDN":"0.0207929033786058","GPRC_IND":"0.422789007425308","GPRC_ISR":"3.97837543487549","GPRC_ITA":"0.221790969371796","GPRC_JPN":"0.34654837846756","GPRC_KOR":"0.429719984531403","GPRC_MEX":"0.180205151438713","GPRC_MYS":"0.0277238711714745","GPRC_NLD":"0.332686454057694","GPRC_NOR":"0.159412249922752","GPRC_PER":"0.0138619355857372","GPRC_PHL":"0.0415858067572117","GPRC_POL":"0.159412249922752","GPRC_PRT":"0.0138619355857372","GPRC_RUS":"2.06542825698853","GPRC_SAU":"0.422789007425308","GPRC_SWE":"0.166343227028847","GPRC_THA":"0.0346548371016979","GPRC_TUN":"0.0138619355857372","GPRC_TUR":"0.602994203567505","GPRC_TWN":"0.207929030060768","GPRC_UKR":"1.64263927936554","GPRC_USA":"5.37843084335327","GPRC_VEN":"0.0346548371016979","GPRC_VNM":"0.117826446890831","GPRC_ZAF":"0.0415858067572117"
}

dati = pd.DataFrame()
for nome in elenco.index:
    df = pd.read_csv(elenco.loc[nome,"url"], index_col=0)
    df.index = pd.to_datetime(df.index)
    dati = pd.concat([dati,df], axis=1)
dati = dati.resample('ME',label="right").last().to_period("M") 

rendimenti = dati.pct_change(fill_method=None)
dati2 = dati.drop(columns=eliminati2)
rendimenti2 = rendimenti.drop(columns=eliminati2)

c = combinations(dati2.columns,5)

r = []
i = []
gpr_values = []

for k in c:
    kk = list(k)
    
    # Calcola GPR automaticamente
    gpr_sum, relevant_codes = calculate_gpr_sum(kk, gpr_data)
    
    print(f"📊 Portfolio: {kk}")
    print(f"🔢 GPR Sum: {gpr_sum:.2f}")
    print(f"📋 GPR Codes: {len(relevant_codes)} codes")
    print("-" * 50)
    
    # Filtra per GPR < 25
    if gpr_sum > 25:
        continue
    else:
        i.append(str(kk))
        r.append(portfolio_yearly_returns(kk,mesi))
        gpr_values.append(gpr_sum)

results = pd.DataFrame(r,index=i,columns=["return","vol","valid"])
results["GPR"] = gpr_values
results["Sharpetti"] = results["return"]/results["vol"]

print("\n" + "="*60)
print("TOP 10 PORTFOLIOS BY SHARPE RATIO")
print("="*60)
print(results.nlargest(columns="Sharpetti",n=10))

print("\n" + "="*60)
print("TOP 10 PORTFOLIOS BY LOWEST GPR")
print("="*60)
print(results.nsmallest(columns="GPR",n=10))

print("\n" + "="*60)
print("PORTFOLIO STATISTICS")
print("="*60)
print(f"Total portfolios analyzed: {len(results)}")
print(f"Average GPR: {results['GPR'].mean():.2f}")
print(f"Average Sharpe Ratio: {results['Sharpetti'].mean():.4f}")
print(f"Average Return: {results['return'].mean():.4f}")
print(f"Average Volatility: {results['vol'].mean():.4f}")