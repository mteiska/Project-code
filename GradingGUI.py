from calendar import c
from lib2to3.pytree import Node
from turtle import left, right
import PySimpleGUI as sg
import os
import sys

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

starting_path = sg.popup_get_folder('Anna näytettävä kansio')

if not starting_path:
    sys.exit(0)

### Create Tree Structure for problems ###
treedata = sg.TreeData()

treedata.Insert("", 'Tietorakenne', 'Tietorakenne',
    ['import ei ole päätasolla', 'import ei tiedoston alussa (ei ennen aliohjelmia ja luokkia)','Lähdekooditiedostoja puuttuu',
    'Pääohjelmatiedostossa vain kutsu kirjastoon'])
treedata.Insert("Tietorakenne", 'import ei ole päätasolla', 'import ei ole päätasolla', [0])
treedata.Insert("Tietorakenne", 'import ei tiedoston alussa (ei ennen aliohjelmia ja luokkia)', 
    'import ei tiedoston alussa (ei ennen aliohjelmia ja luokkia)', [0])
treedata.Insert("", "Poikkeustenkäsittely","Poikkeustenkäsittely",values=[0])
treedata.Insert("Poikkeustenkäsittely","Exceptissä väärä virhetyyppi tiedostonkäsittelyssä",
    "Exceptissä väärä virhetyyppi tiedostonkäsittelyssä",values=[0])



### Layout for GUI ###
layout = [
   [sg.Tree(data=treedata,
                   headings=['lukumäärä' ],
                   auto_size_columns=True,
                   select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                   num_rows=15,
                   col0_width=15,
                   key='-TREE-',
                   show_expanded=False,
                   pad = (5,5),
                   enable_events=True,
                   expand_x=True,
                   expand_y=True,
                   ),sg.Button('+',key='+'),sg.Button('-',key='-')],
    [sg.Text('Opiskelijapalaute'), sg.Text('Tarkastaja'), sg.Push(), sg.Text('Arvioitavat tiedostot')], 
    [sg.InputCombo(('Harjoitustyön palautus 1', 'Harjoitustyön palautus 2'), size=(20, 1)), 
    sg.InputCombo(('Mika/TA', 'Joku/TA'), size=(15, 1)), sg.Listbox(['HTKirjasto.py', 'HTPaaohjelma.py'], no_scrollbar=False,  s=(15,2))],      
    [sg.ButtonMenu(
    'Ongelmat', menu_def=aliluokka_rakenne, size=(30,1), key = 'virhe')],      
    [sg.Button('Go'), sg.Button('Exit')]  ]  

def add_files_in_folder(parent, dirname):
    files = os.listdir(dirname)
    for f in files:
        fullname = os.path.join(dirname, f)
        if os.path.isdir(fullname):            # if folder, add folder and recurse
            treedata.Insert(parent, fullname, f, values=[])
            add_files_in_folder(fullname, fullname)
        else:
            treedata.Insert(parent, fullname, f, values=[os.stat(fullname).st_size])   

add_files_in_folder('', starting_path)

window = sg.Window('Grading tool', layout, resizable=True)

while True:
    event, values = window.read()
    if event == 'Exit' or sg.WIN_CLOSED:
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
    
    if event == '+':
        if values['-TREE-'][0] in virhelista.keys():
          virhelista[values['-TREE-'][0]] = virhelista[values['-TREE-'][0]] + 1
          print(virhelista[values['-TREE-'][0]])
        else:
            virheen_lukumaara = 1
        
            virhelista[values['-TREE-'][0]] = virheen_lukumaara
            print(virhelista[values['-TREE-'][0]])
        window['-TREE-'].update(key = values['-TREE-'][0],value = virhelista[values['-TREE-'][0]])

    if event == '-':
        if virhelista[values['-TREE-'][0]] >0:
            if values['-TREE-'][0] in virhelista.keys():
                virhelista[values['-TREE-'][0]] = virhelista[values['-TREE-'][0]] - 1
                print(virhelista[values['-TREE-'][0]])
            else:
                virheen_lukumaara = 1
        
                virhelista[values['-TREE-'][0]] = virheen_lukumaara
                print(virhelista[values['-TREE-'][0]])
            window['-TREE-'].update(key = values['-TREE-'][0],value = virhelista[values['-TREE-'][0]])
       
       

  
      

 