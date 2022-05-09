from calendar import c
from lib2to3.pytree import Node
from turtle import left, right
import PySimpleGUI as sg
import os
import sys
import pandas as pd
import csv

#Just for testing how to get files in directory    
#files_in_directory = os.listdir('C:/Users/mika.teiska@lut.fi/Downloads/OP_HT_Palautus1/HT_Palautus1_palautukset/minimi')
#print(files_in_directory)
sg.theme('BlueMono')      
virhelista = {}
basenames=[]
virheen_lukumaara = 0    
aliluokka_rakenne=[
    'Alaluokat',['TiedostoRakenne',
    ['import ei ole päätasolla', 'import ei tiedoston alussa (ei ennen aliohjelmia ja luokkia)','Lähdekooditiedostoja puuttuu',
    'Pääohjelmatiedostossa vain kutsu kirjastoon'],
    'Tiedostonkäsittely',
    [['Tiedosto sulkematta'],
    ]]]

class Virhetiedot:
    virhe = "",
    vakavuus = 0
    lukumaara = 0


starting_path = sg.popup_get_folder('Anna näytettävä kansio')

if not starting_path:
    sys.exit(0)

### Create Tree Structure for problems ###
treedata = sg.TreeData()
treedata.Insert("", 'Toiminnallisuus', 'Toiminnallisuus',
    [0])
treedata.Insert("Toiminnallisuus", 'Kovakoodattu tuloksia', 'Kovakoodattu tuloksia', [0])
treedata.Insert("Toiminnallisuus", 'Kovakoodattu tiedoston nimi', 'Kovakoodattu tiedoston nimi', [0])
treedata.Insert("Toiminnallisuus", 'Kovakoodattu päivämäärä', 'Kovakoodattu päivämäärä', [0])
treedata.Insert("", 'Tietorakenne', 'Tietorakenne',
    [0])
treedata.Insert("Tietorakenne", 'import ei ole päätasolla', 'import ei ole päätasolla', [0])
treedata.Insert("Tietorakenne", 'import ei tiedoston alussa (ei ennen aliohjelmia ja luokkia)', 
    'import ei tiedoston alussa (ei ennen aliohjelmia ja luokkia)', [0])
treedata.Insert("", "Poikkeustenkäsittely","Poikkeustenkäsittely",values=[0])
treedata.Insert("Poikkeustenkäsittely","Exceptissä väärä virhetyyppi tiedostonkäsittelyssä",
    "Exceptissä väärä virhetyyppi tiedostonkäsittelyssä",values=[0])



### Layout for GUI ###
layout = [
    [sg.Push(),sg.Text('Laita virheen koodi tähän.')],
   [sg.Tree(data=treedata,
                   headings=['lukumäärä' ],
                   auto_size_columns=False,
                   select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                   num_rows=15,
                   col0_width=15,
                   key='-TREE-',
                   show_expanded=False,
                   pad = (5,5),
                   enable_events=True,
                   expand_x=True,
                   expand_y=True,
                   ),sg.Button('+',key='+'),sg.Button('-',key='-'), sg.Multiline(key = 'virheteksti', size = (20,10))],
   
    [sg.Text('Opiskelijapalaute'), sg.Text('Tarkastaja'), sg.Push(), sg.Text('Arvioitavat tiedostot')], 
    [sg.InputCombo(('Harjoitustyön palautus 1', 'Harjoitustyön palautus 2'), size=(20, 1)), 
    sg.InputCombo(('Mika/TA', 'Joku/TA'), size=(15, 1)), sg.Listbox(['HTKirjasto.py', 'HTPaaohjelma.py'], no_scrollbar=False,  s=(15,2))],      
    [sg.ButtonMenu(
    'Ongelmat', menu_def=aliluokka_rakenne, size=(30,1), key = 'virhe')],      
    [sg.Button('Laske virhepisteet'), sg.Button('Exit')]  ]  

def add_files_in_folder(parent, dirname):
    files = os.listdir(dirname)
    for f in files:
        fullname = os.path.join(dirname, f)
        if os.path.isdir(fullname):            # if folder, add folder and recurse
            treedata.Insert(parent, fullname, f, values=[])
            add_files_in_folder(fullname, fullname)
        else:
            treedata.Insert(parent, fullname, f, values=[os.stat(fullname).st_size])   

### Protyping for error score calculating ###
def read_csv_and_make_object(file):
    read_file = pd.read_excel ('//maa1.cc.lut.fi/home/h18439/Desktop/Project code/arviointiohjeet_HT.xlsx')
    read_file.to_csv ('//maa1.cc.lut.fi/home/h18439/Desktop/Project code/arviointiohjeet_HT.csv', index = None, header=True)
    
    lista = []
   
 
    with open('arviointiohjeet_HT.csv',"r", encoding ="utf-8") as csv_file:
          csv_file.readline()
          csv_reader = csv.reader(csv_file, delimiter=",")
          for row in csv_reader:
            if row == ['', '', '', '', '', '', '', '', '', '']:
                continue
            if row:
                print (row)

       
                
      
        
                v = Virhetiedot()
               
        
           
                if row[1] == "" and row[3] != 'Ei yhtään oikein' and row[3] != 'Kaikista':
                    v.virhe = lista[len(lista)-1].virhe
                    v.vakavuus = float(row[2]) 
                    v.lukumaara = float(row[3])
                    lista.append(v)
                
            
                else:
                    if (row[3] == 'Ei yhtään oikein' or row[3] == 'Kaikista'):
                        row[3] = 100.0
                   
                    if '?' in row[2]:
                        print(row[2])
                        row[2] = row[2][:-1]
                    v.virhe = row[1]
                    v.vakavuus = float(row[2])
                    v.lukumaara = float(row[3])
                    lista.append(v)
    
        
      
        
      
           
    for i in lista:
        print(i.virhe, i.vakavuus, i.lukumaara)
    return lista
    #When we have list we can comapre it to programs dict and get the error score
            



        
def main():
    virhepisteet = 0
    add_files_in_folder('', starting_path)
    list = read_csv_and_make_object('//maa1.cc.lut.fi/home/h18439/Desktop/Project code/arviointiohjeet_HT.xlsx')
    window = sg.Window('Grading tool', layout, resizable=True)

    while True:
        event, values = window.read()
        
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        if event == 'virhe':
            if values['virhe'] in virhelista.keys():
                virhelista[values['virhe']] = virhelista[values['virhe']] + 1
                print(virhelista[values['virhe']])
            else:
                virheen_lukumaara = 1
                print(values['virhe'])
                virhelista[values['virhe']] = virheen_lukumaara
                print(virhelista[values['virhe']])
        print(event, "Values are these after this:", values)
        
        if event == '+' or event == '-':
            if event=='+':
                if values['-TREE-'][0] in virhelista.keys():
                    virhelista[values['-TREE-'][0]] = virhelista[values['-TREE-'][0]] + 1
                else:
                    virheen_lukumaara = 1
                    virhelista[values['-TREE-'][0]] = virheen_lukumaara
                
            if event== '-':
                if virhelista[values['-TREE-'][0]] >0:
                    if values['-TREE-'][0] in virhelista.keys():
                        virhelista[values['-TREE-'][0]] = virhelista[values['-TREE-'][0]] - 1
                else:
                    virheen_lukumaara = 1
                    virhelista[values['-TREE-'][0]] = virheen_lukumaara

            window['-TREE-'].update(key = values['-TREE-'][0], value = virhelista[values['-TREE-'][0]])
        if  event == 'Laske virhepisteet':
            for virhe in list:
                
                if virhe.virhe in virhelista.keys():
                    print("Listalla virheiden lukumäärä: ", virhe.lukumaara)
                    print(virhelista[values['-TREE-'][0]])
                    if int(virhe.lukumaara) <= virhelista[values['-TREE-'][0]]:
                        virhepisteet = virhepisteet + virhe.vakavuus
                        print("Virheen pisteet ovat :",virhepisteet)



main()

        
        
          
       

  
      

 