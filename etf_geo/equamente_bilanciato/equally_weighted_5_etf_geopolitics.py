import pandas as pd
import numpy as np
import copy
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
import openai
import json

def portfolio_yearly_returns(which,months): # non ribilanciato!
    rendimenti = ( dati[which] / dati[which].shift(months) ).mean(axis=1)
    return ( rendimenti.mean(axis=0)**(12/months) -1 )  , rendimenti.std(axis=0), rendimenti.count().sum() 

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
for k in c:
    kk = list(k)
    # print(kk)
    i.append(str(kk))
    prompt = f"Data la seguente lista di paesi: {kk}, restituisci solo la **somma** dei rispettivi indici GRU, senza spiegazioni, solo il numero."
    functions = [{
        "name": "sum_gru",
        "description": "Restituisce la somma dei valori GRU",
        "parameters": {
            "type": "object",
            "properties": {
                "sum": {
                    "type": "number",
                    "description": "La somma totale degli indici GRU"
                }
            },
            "required": ["sum"]
        }
    }]
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Sei un assistente che restituisce solo risultati numerici."},
            {"role": "user", "content": prompt}
        ],
        functions=functions,
        function_call={"name": "sum_gru"},
        temperature=0,
        max_tokens=20
    )
    args = json.loads(response.choices[0].message.function_call.arguments)
    gru_sum = args["sum"]
    print(f"🔢 Somma indici GRU per {kk}: {gru_sum:.2f}")
    if gru_sum > 2.5:
        continue
    else:
        r.append(portfolio_yearly_returns(kk,mesi))
    #if len(i)%1000==0: print(len(i), end=" ")
results = pd.DataFrame(r,index=i,columns=["return","vol","valid"])
results["Sharpetti"] = results["return"]/results["vol"]

print(results.nlargest(columns="Sharpetti",n=10))