from lib2to3.pytree import Node
import PySimpleGUI as sg
import os
import sys
import csv
import json
from io import BytesIO
from PIL import Image, ImageDraw

sg.theme('BlueMono')      

class Virhetiedot:
    virhe = "",
    vakavuus = 0
    lukumaara = 0
treedata = sg.TreeData()

def initiate_problem_list():
    lista = []
    f = open('Problem_list.json', encoding = 'utf-8')
    virheet = json.load(f)

    category = virheet['violations'][0]['category']
    
    treedata.Insert("", 'Toiminnallisuus', 'Toiminnallisuus',
        [0])
    for i in virheet['violations']:
        if category != i['category']:
            treedata.Insert("", i['category'], i['category'],[0])
            treedata.Insert(i['category'], i['ID'], i['text'], [0])
            v = Virhetiedot()
            category = i['category']
        else:
            treedata.Insert(i['category'], i['ID'], i['text'], [0])
            v = Virhetiedot()
            v.virhe = i['ID']
            v.vakavuus = i['error_values']
            v.lukumaara = i['error_values'].keys()
            lista.append(v)
    return lista
starting_path = sg.popup_get_folder('Anna näytettävä kansio')

if not starting_path:
    sys.exit(0)

### Create Tree Structure for problems ###

studentdata = sg.TreeData()

            ### Layout for GUI ####
layout = [[sg.Text('Opiskelijat')],
         [sg.Tree(data=studentdata,
                   headings=[],
                   auto_size_columns=True,
                   select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                   num_rows=7,
                   col0_width=8,
                   key='-PROGRAMS-',
                   show_expanded=False,
                   pad = (2,2),
                   enable_events=True,
                   expand_x=True,
                   expand_y=True,
                   row_height=30
                   
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
                   
                   headings=['lkm' ],
                   auto_size_columns=True,
                   select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                   num_rows=12,
                  
                   col0_heading = 'Ongelmat koodissa',
                    col0_width = 25,
                   key='-TREE-',
                   show_expanded=True,
                   pad = (2,2),
                   enable_events=True,
                   expand_x=True,
                   expand_y=True,
                   ),sg.Button('+',key='+'),sg.Button('-',key='-'), sg.Button('Ei yhtään oikein', key = 'ALL'), sg.Multiline(key = 'virheteksti', size = (20,10)), ],
                   
   
        [sg.Text('Opiskelijapalaute'), sg.Text('Tarkastaja'), sg.Push(), sg.Text('Arvioitavat tiedostot')], 
        [sg.InputCombo(('Harjoitustyön Palautus 1', 'Harjoitustyön Palautus 2', 'Korjaus Palautus'), size=(20, 1)), 
            sg.InputCombo(('Mika/TA', 'Joku/TA'), size=(15, 1))],      
        [sg.Button('Laske virhepisteet'), sg.Button('Tallenna', key = 'SAVE'), 
        sg.Button('Kirjoita arvostellut työt tiedostoon', key='WRITE'), sg.Button('Exit')]  ]  
#################################################################################################

def add_files_in_folder(parent, dirname):
    files = os.listdir(dirname)
    for f in files:
        fullname = os.path.join(dirname, f).replace("\\","/")
        if os.path.isdir(fullname):            # if folder, add folder and recurse
            studentdata.Insert(parent, fullname, f, values=[0], icon = check[0])
            add_files_in_folder(fullname, fullname)
        else:
            studentdata.Insert(parent, fullname, f, values=[0], icon = check[0])
### Updating already reviewed programs list ####           
def update_tree_data(students):
    ready_studentdata = sg.TreeData()
    for id in students:
        ready_studentdata.Insert('',id,id,values=[])
    return ready_studentdata

### Nice to have function for finding selected elements key ###
def key_define(tree):
    item =  tree.Widget.selection()
    return '' if len(item) == 0 else tree.IdToKey[item[0]]
###############################################################
def double_click(tree):
    item = tree.Widget.selection()[0]
    key = tree.IdToKey[item]
    print("AVAIN ON SEURAAVA DOUBLE CLICKISTÄ" ,key)
    print(studentdata.tree_dict[key].values[-1])
    index = studentdata.tree_dict[key].values[0]
    index = (index + 1) % 3
    studentdata.tree_dict[key].values[-1] = index
    tree.update(key=key, icon=check[index])

def icon(check):
    box = (32, 32)
    background = (255, 255, 255, 0)
    rectangle = (3, 3, 29, 29)
    line = ((9, 17), (15, 23), (23, 9))
    im = Image.new('RGBA', box, background)
    draw = ImageDraw.Draw(im, 'RGBA')
    draw.rectangle(rectangle, outline='black', width=3)
    if check == 1:
        draw.line(line, fill='black', width=3, joint='curve')
    elif check == 2:
        draw.line(line, fill='grey', width=3, joint='curve')
    with BytesIO() as output:
        im.save(output, format="PNG")
        png = output.getvalue()
    return png

check = [icon(0), icon(1), icon(2)] # Three states Ready, In Progress, Unchecked
#WIP: Usability of In Progress state
### Protyping for error score calculating ###

def mergedicts(dict1, dict2, student):
    dict2[student] = dict(dict1)
    print(dict2)
    

       
def main():
    virhelista = {}
    virheen_lukumaara = 0   
    students = {} 
    virhepisteet = 0
    add_files_in_folder('', starting_path)
    list = initiate_problem_list()
    window = sg.Window('Grading tool', layout, resizable=True, finalize = True)
    
    tree = window['-PROGRAMS-']         # type: sg.Tree
    tree.bind("<Double-1>", '+DOUBLE')  
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
        ### WIP: Counting mistakepoints right, taking account different constraints
       
        if  event == 'Laske virhepisteet':
            for virhe in list:
                
                if virhe.virhe in virhelista.keys():
                    print("Listalla virheiden lukumäärä: ", virhe.lukumaara, "Virheen vakavuus: ", virhe.vakavuus)
                    print(virhelista[values['-TREE-'][0]])
                    for i in virhe.lukumaara:
                        if i == 'All' and virhelista[values['-TREE-'][0]]==-1:
                            virhepisteet = virhepisteet + int(virhe.vakavuus[i])
                            continue
                        elif i == 'All':
                            continue
                        if int(i) <= virhelista[values['-TREE-'][0]]:
                            virhepisteet = virhepisteet + int(virhe.vakavuus[i])
                            print("Virheen pisteet ovat :",virhepisteet)
       ### All occurances are wrong ###
        if event == 'ALL':
            window['-TREE-'].update(key = values['-TREE-'][0], value = -1)
            virhelista[values['-TREE-'][0]] = -1 ## -1 is easy repsesentation for all being wrong
        ### If row selected and to dict ###
        if event == '-PROGRAMS-':
            key = key_define(tree)
            
            node = studentdata.tree_dict[key]
            parent_node = studentdata.tree_dict[node.parent]
            if node.parent == '':
                continue
            
            if(values['-PROGRAMS-'][0]!= node.parent):
                path2 = values['-PROGRAMS-'][0].split('/')
                path2 = path2[len(path2)-2]
                if not students:
                    students[path2] = []
                if path2 not in students:
                    students[path2] = []
            window['-TREE-'].update(values = treedata)
            if virhelista:  #check if dict exists
                virhelista.clear()
               #virhelista = dict.fromkeys(virhelista, 0)
###Adding checkboxes next to student names for easier marking ###
        if event.endswith('DOUBLE'):
            double_click(tree)
                
        ### Save added rows to other tree structure ###
        if event == 'SAVE':
            print("Paluuarvot programsista on : ", values['-PROGRAMS-'][0])
            
            paluuarvo = update_tree_data(students)
            window['-READY-'].update(values=paluuarvo)
            mergedicts(virhelista,students, path2)
          
        if event == 'WRITE':
            with open("Arvostellut.json", "w") as outfile:
                json.dump(students, outfile, indent=4)
           
            
        # Example dict structure after nesting #
        #{Opiskelija: {virhekoodi1: lkm1}, Opiskelija2: {Virhekoodi2: lkm2, virhekoodi3 : lkm3}}

main()

        
        
          
       

  
      

 
        
          
       

  
      

 