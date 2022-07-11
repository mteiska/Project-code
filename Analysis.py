from operator import index
from sqlite3 import Row
import PySimpleGUI as sg # Not default library
import pandas as pd
import json
import matplotlib.pyplot as plt

#V0.0.1 Data is more machine readable now 
def main():
    with open('Arvostellut.json','r', encoding = 'utf-8') as f:
        data = json.loads(f.read())
    
    df2 = pd.DataFrame([data])
    print(data)

    print(df2.T)
    df2 = df2.T
    print(df2)
    
    df2['Opiskelija_data'] = df2[0].apply(lambda x : break_dict(x))
    df2 = df2.explode('Opiskelija_data')
    df2['virhekoodi'],df2['määrä'] = df2['Opiskelija_data'].str
    df2.columns = ['joku', 'Opiskelija_data', 'virhekoodi', 'määrä']
    df2 = df2.drop(columns=['joku','Opiskelija_data'])
    print(df2)
    
    df2['virhekoodit']=df2['määrä'][df2['virhekoodi']=='virhekoodi']
    df2 = df2[df2['virhekoodi'] != 'virhekoodi']
    df2['virhepisteet']=df2['määrä'][df2['virhekoodi']=='virhepisteet']
    df2 = df2[df2['virhekoodi'] != 'virhepisteet']
    df2.fillna(0, inplace=True)
    print(df2[df2['virhekoodi'].str.startswith("PK", na = False)])
    dfg = df2.groupby('virhekoodi')['määrä'].agg('sum').reset_index()
    print(dfg)
    dfg.plot(x = 'virhekoodi', y = 'määrä', kind='bar')
    plt.show()
def break_dict(data):
    lista = []
    for key in data:
        lista.append((key, data[key]))
        
    return lista
    

main()