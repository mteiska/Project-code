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
students = {} 

class Virhetiedot:
    virhe = "",
    vakavuus = 0
    lukumaara = 0

starting_path = sg.popup_get_folder('Anna näytettävä kansio')

if not starting_path:
    sys.exit(0)

### Create Tree Structure for problems ###

studentdata = sg.TreeData()

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
layout = [[sg.Text('Opiskelijat')],
         [sg.Tree(data=studentdata,
                   headings=[],
                   auto_size_columns=True,
                   select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                   num_rows=15,
                   col0_width=7,
                   key='-PROGRAMS-',
                   show_expanded=False,
                   pad = (2,2),
                   enable_events=True,
                   expand_x=True,
                   expand_y=True,
                   ),
        sg.Tree(data=studentdata,
                   headings=[],
                   auto_size_columns=True,
                   select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                   num_rows=15,
                   col0_width=7,
                   key='-READY-',
                   show_expanded=False,
                   pad = (2,2),
                   enable_events=True,
                   expand_x=True,
                   expand_y=True,
                   )
                   ],

    [sg.Push(),sg.Text('Laita virheen koodi tähän.')],
   [sg.Tree(data=treedata,
                   headings=['lukumäärä' ],
                   auto_size_columns=False,
                   select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                   num_rows=15,
                   col0_width=12,
                   key='-TREE-',
                   show_expanded=False,
                   pad = (5,5),
                   enable_events=True,
                   expand_x=True,
                   expand_y=True,
                   ),sg.Button('+',key='+'),sg.Button('-',key='-'), sg.Button('Ei yhtään oikein', key = 'ALL'), sg.Multiline(key = 'virheteksti', size = (20,10)), ],
                   
   
        [sg.Text('Opiskelijapalaute'), sg.Text('Tarkastaja'), sg.Push(), sg.Text('Arvioitavat tiedostot')], 
        [sg.InputCombo(('Harjoitustyön palautus 1', 'Harjoitustyön palautus 2'), size=(20, 1)), 
            sg.InputCombo(('Mika/TA', 'Joku/TA'), size=(15, 1)), sg.Listbox(['HTKirjasto.py', 'HTPaaohjelma.py'], no_scrollbar=False,  s=(15,2))],      
        [sg.Button('Laske virhepisteet'), sg.Button('Tallenna', key = 'SAVE'), sg.Button('Exit')]  ]  


def add_files_in_folder(parent, dirname):
    files = os.listdir(dirname)
    for f in files:
        fullname = os.path.join(dirname, f).replace("\\","/")
        if os.path.isdir(fullname):            # if folder, add folder and recurse
            studentdata.Insert(parent, fullname, f, values=[])
            add_files_in_folder(fullname, fullname)
        else:
            studentdata.Insert(parent, fullname, f, values=[])
            
def update_tree_data(students):
    ready_studentdata = sg.TreeData()
    for id in students:
        ready_studentdata.Insert('',id,id,values=[])
    return ready_studentdata

def key_define(tree):
    item =  tree.Widget.selection()
    return '' if len(item) == 0 else tree.IdToKey[item[0]]





### Protyping for error score calculating ###
def read_csv_and_make_object(file):
    read_file = pd.read_excel ('//maa1.cc.lut.fi/home/h18439/Desktop/Project code/arviointiohjeet_HT.xlsx')
    read_file.to_csv ('arviointiohjeet_HT.csv', index = None, header=True, encoding='utf-8')
    
    lista = []
 
    with open('//maa1.cc.lut.fi/home/h18439/Desktop/Project code/arviointiohjeet_HT.csv',"r", encoding ="utf-8") as csv_file:
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
        studenttree = window['-PROGRAMS-']
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
        ### Adding to problem counter ###
        if event == '+' or event == '-':
            if event=='+':
                if values['-TREE-'][0] in virhelista.keys():
                    virhelista[values['-TREE-'][0]] = virhelista[values['-TREE-'][0]] + 1
                else:
                    virheen_lukumaara = 1
                    virhelista[values['-TREE-'][0]] = virheen_lukumaara
          ### Decreasing problem counter ###      
            if event== '-':
                if virhelista[values['-TREE-'][0]] >0:
                    if values['-TREE-'][0] in virhelista.keys():
                        virhelista[values['-TREE-'][0]] = virhelista[values['-TREE-'][0]] - 1
                else:
                    virheen_lukumaara = 1
                    virhelista[values['-TREE-'][0]] = virheen_lukumaara

            window['-TREE-'].update(key = values['-TREE-'][0], value = virhelista[values['-TREE-'][0]])
        ### WIP: Counting mistakepoints but not finished
        ### Needs JSON implementation
        if  event == 'Laske virhepisteet':
            for virhe in list:
                
                if virhe.virhe in virhelista.keys():
                    print("Listalla virheiden lukumäärä: ", virhe.lukumaara, "Virheen vakavuus: ", virhe.vakavuus)
                    print(virhelista[values['-TREE-'][0]])
                    if int(virhe.lukumaara) <= virhelista[values['-TREE-'][0]]:
                        virhepisteet = virhepisteet + virhe.vakavuus
                        print("Virheen pisteet ovat :",virhepisteet)
       ### All occurances are wrong ###
        if event == 'ALL':
            window['-TREE-'].update(key = values['-TREE-'][0], value = 'Kaikki')
            virhelista[values['-TREE-'][0]] = 0
        ### If row selected and to dict ###
        if event == '-PROGRAMS-':
            key = key_define(studenttree)
            
            node = studentdata.tree_dict[key]
            parent_node = studentdata.tree_dict[node.parent]
            if node.parent == '':
                continue
            if(values['-PROGRAMS-'][0]!= node.parent):
                if not students:
                    students[values['-PROGRAMS-'][0]] = []
                if values['-PROGRAMS-'][0] not in students:
                    students[values['-PROGRAMS-'][0]] = []
                print(node.parent)
        ### Save added rows to other tree structure ###
        if event == 'SAVE':
            print("Paluuarvot programsista on : ", values['-PROGRAMS-'][0])
            
            paluuarvo = update_tree_data(students)
            window['-READY-'].update(values=paluuarvo)

            

        



main()

        
        
          
       

  
      

 
        
          
       

  
      

 