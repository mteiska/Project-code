from operator import index
from sqlite3 import Row
import PySimpleGUI as sg # Not default library
import pandas as pd
import json
import matplotlib.pyplot as plt

#V0.0.1 Data is more machine readable now 
#V0.0.2 Made graph and changed ticks for it.
def main():
    with open('Arvostellut.json','r', encoding = 'utf-8') as f:
        data = json.loads(f.read())
    
    df = pd.DataFrame([data])

    print(df.T)
    df = df.T
    df['Opiskelija_data'] = df[0].apply(lambda x : break_dict(x))
    df = df.explode('Opiskelija_data')
    df['virhekoodi'],df['määrä'] = df['Opiskelija_data'].str
    df.columns = ['joku', 'Opiskelija_data', 'virhekoodi', 'määrä']
    df = df.drop(columns=['joku','Opiskelija_data'])
    print(df)
    
    df['virhekoodit']=df['määrä'][df['virhekoodi']=='virhekoodi']
    df = df[df['virhekoodi'] != 'virhekoodi']
    df['virhepisteet']=df['määrä'][df['virhekoodi']=='virhepisteet']
    df = df[df['virhekoodi'] != 'virhepisteet']
    df.fillna(0, inplace=True)
    print(df[df['virhekoodi'].str.startswith("PK", na = False)])
    dfg = df.groupby('virhekoodi')['määrä'].agg('sum').reset_index()
    print(dfg)
     
    ax =dfg.plot(x = 'virhekoodi', y = 'määrä', kind='bar')
    ax.yaxis.get_major_locator().set_params(integer=True)
    ax.yaxis.set_major_locator(plt.MaxNLocator(10))
    plt.show()


def break_dict(data):
    lista = []
    for key in data:
        lista.append((key, data[key]))
        
    return lista
    

main()