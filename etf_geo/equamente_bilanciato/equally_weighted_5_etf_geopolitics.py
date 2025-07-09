import pandas as pd
import numpy as np
import copy
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
import openai
import json
import time
import random

#gpr origin: https://policyuncertainty.com/gpr.html

def portfolio_yearly_returns(which,months): # non ribilanciato!
    rendimenti = ( dati[which] / dati[which].shift(months) ).mean(axis=1)
    return ( rendimenti.mean(axis=0)**(12/months) -1 )  , rendimenti.std(axis=0), rendimenti.count().sum() 


TPM_LIMIT = 30000   
TOKENS_PER_CALL = 1011 
base_delay = 60.0 * TOKENS_PER_CALL / TPM_LIMIT

pd.set_option('display.max_colwidth', None)
openai.api_key = "..."
mesi = 60 #5 anni
eliminati2 = ["ACWI","USA","NORTH AMERICA","WORLD ex EMU", "WORLD ex EUROPE", "EM (EMERGING MARKETS)", "EM ASIA",
             "EM (EMERGING MARKETS) ex CHINA", "EM ASIA", "AC FAR EAST ex JAPAN", "AC ASIA ex JAPAN", "EMU", "WORLD ex USA",
             "EUROPE ex UK", "FRANCE", "JAPAN", "EM LATIN AMERICA", "EMU SMALL CAP", "AUSTRALIA", "UNITED KINGDOM SMALL CAP", "POLAND"]

urlo = "https://raw.githubusercontent.com/paolocole/Stock-Indexes-Historical-Data/main/DAILY/NET/EUR/"
elenco = pd.read_excel("https://www.paolocoletti.com/wp-content/uploads/youtube/etfs_with_msci.xlsx" , sheet_name="selezionati" , index_col=0)
elenco["url"] = urlo + elenco["Path"] + "/" + elenco["File"] + ".csv"
elenco["url"] = elenco["url"].str.replace("\\","/") 


dati = pd.DataFrame()
for nome in elenco.index:
    #print(nome, end=" - ")
    df = pd.read_csv(elenco.loc[nome,"url"], index_col=0)
    df.index = pd.to_datetime(df.index)
    dati = pd.concat([dati,df], axis=1)
dati = dati.resample('ME',label="right").last().to_period("M") 

rendimenti = dati.pct_change(fill_method=None)
dati2 = dati.drop(columns=eliminati2)
rendimenti2 = rendimenti.drop(columns=eliminati2)
#print(dati2.columns)

c = combinations(dati2.columns,5)

r = []
i = []
path = "/Users/riccardomarega/Desktop/market_evaluations/etf_geo/equamente_bilanciato/gpr_stati.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)
for k in c:
    print('API in fase di processazzione')
    delay = base_delay * random.uniform(1.0, 1.2)
    time.sleep(delay)
    kk = list(k)
    i.append(str(kk))
    association_prompt = (
        f"Dato questo JSON con codici GPR dei paesi:\n"
        f"{data}\n\n"
        f"E questa lista di ETF/indici: {kk}\n\n"
        "Per ogni ETF/indice nella lista, identifica quali codici GPR (GPRC_XXX) dovrebbero essere inclusi "
        "basandoti sui nomi dei paesi/regioni. Ad esempio:\n"
        "- WORLD = tutti i codici GPR\n"
        "- EUROPE = codici GPR dei paesi europei (DEU, FRA, ITA, ESP, NLD, BEL, etc.)\n"
        "- JAPAN IMI = GPRC_JPN\n"
        "- CHINA = GPRC_CHN\n"
        "- INDIA = GPRC_IND\n"
        "- BRAZIL = GPRC_BRA\n"
        "- CANADA = GPRC_CAN\n"
        "- UNITED KINGDOM = GPRC_GBR\n"
        "- KOREA = GPRC_KOR\n"
        "- TAIWAN = GPRC_TWN\n"
        "- SWITZERLAND = GPRC_CHE\n"
        "- SAUDI ARABIA = GPRC_SAU\n"
        "- MEXICO = GPRC_MEX\n"
        "- NORDIC COUNTRIES = GPRC_SWE, GPRC_NOR, GPRC_DNK, GPRC_FIN\n"
        "- EM (EMERGING MARKETS) = paesi emergenti come CHN, IND, BRA, RUS, etc.\n"
        "- PACIFIC ex JAPAN = paesi del Pacifico escluso il Giappone (AUS, HKG, etc.)\n\n"
        "Restituisci SOLO una lista di tutti i codici GPR unici che dovrebbero essere inclusi, "
        "senza duplicati, nel formato: ['GPRC_XXX', 'GPRC_YYY', ...]"
    )
    
    association_functions = [{
        "name": "get_gpr_codes",
        "description": "Restituisce i codici GPR associati agli ETF/indici",
        "parameters": {
            "type": "object",
            "properties": {
                "gpr_codes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista dei codici GPR da includere"
                }
            },
            "required": ["gpr_codes"]
        }
    }]
    
    print("🔍 Fase 1: Associazione ETF-indice...")
    association_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Sei un esperto di mercati finanziari che associa ETF/indici ai rispettivi paesi."},
            {"role": "user", "content": association_prompt}
        ],
        functions=association_functions,
        function_call={"name": "get_gpr_codes"},
        temperature=0,
        max_tokens=500
    )
    
    association_args = json.loads(association_response.choices[0].message.function_call.arguments)
    relevant_codes = association_args["gpr_codes"]
    
    print(f"📋 Codici GPR identificati: {relevant_codes}")
    
    # Step 2: Calcolo della somma
    sum_prompt = (
        f"Dato questo JSON con dati GPR:\n"
        f"{data}\n\n"
        f"Calcola la somma SOLO dei seguenti codici GPR: {relevant_codes}\n"
        "Restituisci solo il numero della somma, senza spiegazioni."
    )
    
    sum_functions = [{
        "name": "calculate_sum",
        "description": "Calcola la somma dei valori GPR specificati",
        "parameters": {
            "type": "object",
            "properties": {
                "sum": {
                    "type": "number",
                    "description": "La somma totale dei valori GPR specificati"
                }
            },
            "required": ["sum"]
        }
    }]
    
    print("🧮 Fase 2: Calcolo della somma...")
    sum_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Sei un assistente che calcola somme numeriche precise."},
            {"role": "user", "content": sum_prompt}
        ],
        functions=sum_functions,
        function_call={"name": "calculate_sum"},
        temperature=0,
        max_tokens=50
    )
    
    sum_args = json.loads(sum_response.choices[0].message.function_call.arguments)
    gpr_sum = sum_args["sum"]
    
    print(f"🔢 Somma indici GPR per {kk}: {gpr_sum:.2f}")
    print(f"📊 Dettaglio: {len(relevant_codes)} codici inclusi\n")
    if gpr_sum > 25:
        continue
    else:
        r.append(portfolio_yearly_returns(kk,mesi))
    #if len(i)%1000==0: print(len(i), end=" ")
results = pd.DataFrame(r,index=i,columns=["return","vol","valid"])
results["Sharpetti"] = results["return"]/results["vol"]

print(results.nlargest(columns="Sharpetti",n=10))