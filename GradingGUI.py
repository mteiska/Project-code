from lib2to3.pytree import Node
from multiprocessing.sharedctypes import Value
from tkinter import E, Scrollbar
import PySimpleGUI as sg # Not default library
import os
import sys
import csv
import json
from io import BytesIO
from PIL import Image, ImageDraw

#V1.1.1 added constraints to mistake calculations + fixed issues when student not chosen.
sg.theme('BlueMono')      
font = ("Arial", 11)
class Virhetiedot:
    virhe = "",
    vakavuus = 0
    lukumaara = 0
    alternative = []

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
            if 'alternatives' in i:
                v.alternative = i['alternatives']
            lista.append(v)
    return lista
starting_path = sg.popup_get_folder('Anna näytettävä kansio')

if not starting_path:
    sys.exit(0)

### Create Tree Structure for problems ###
studentdata = sg.TreeData()
###Create menu for MenuBar ### 
menu_def = [['Toiminto',['Export opiskelijadata', 'Laske virhepisteet']]]

treecol = [[sg.Tree(data=studentdata,
                   headings=[],
                   auto_size_columns=True,
                   select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                   num_rows=7,
                   col0_width=50,
                   key='-PROGRAMS-',
                   show_expanded=False,
                   pad = (2,2),
                   enable_events=True,
                   expand_x=False,
                   expand_y=True,
                   row_height=30
                   
                   ), sg.Multiline(key = 'virheteksti', autoscroll = True, size = (25,10)), 
                   sg.Multiline(key = "-ERROROUT-",autoscroll = True, size = (25,10))
                   ],[sg.Tree(data=treedata,
                   headings=['lkm' ],
                   auto_size_columns=True,
                   select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                   num_rows=15,
                
                   col0_heading = 'Ongelmat koodissa                    ',
                   col0_width = 55,
                   key='-TREE-',
                   show_expanded=False,
                   pad = (2,2),
                   enable_events=True,
                   expand_x=True,
                   expand_y=True
                   )],
                   [sg.Button('Tallenna', key = 'SAVE'), 
        sg.Button('Kirjoita arvostellut työt tiedostoon', key='WRITE'), sg.Button('Exit')]]

buttoncol = [
               
                [sg.Button('+',key='+'),sg.Button('-',key='-'),], 
                [sg.Button('Ei yhtään oikein', key = 'ALL')],
                [sg.Text('Virhepisteet ovat:'), sg.Txt(key = '-virheout-', text = 0)] 
                ]
            ### Layout for GUI ####
layout = [[sg.MenuBar(menu_def, tearoff=False),sg.Text('Opiskelijat'),  sg.Text("        " *13), 
sg.Text('Laita virheen koodi alle.'), sg.pin(sg.Button("<-",  enable_events = True, key = "-LEFT-")), sg.Button("->", enable_events = True, key = "-RIGHT-")],
            [sg.Column(treecol, expand_y = True), sg.Column(buttoncol)],
            [sg.Text('Opiskelijapalaute'), sg.Text("      " *2), sg.Text('Tarkastaja')],
        [sg.InputCombo(('Harjoitustyön Palautus 1', 'Harjoitustyön Palautus 2', 'Korjaus Palautus'), size=(20, 1)), 
            sg.InputCombo(('Mika/TA', 'Joku/TA'), size=(15, 1))],      
        ]  
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
### Updating already reviewed programs list since not needed commented ####           
# def update_tree_data(students):
#     ready_studentdata = sg.TreeData()
#     for id in students:
#         ready_studentdata.Insert('',id,id,values=[])
#     return ready_studentdata

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


def mergedicts(dict1, dict2, student):
    if dict2[student] != []:
        print("TULEE MERGEN SISÄSLTÄ", dict2[student])
        dict2[student].update(dict1)

    elif dict1 != {}:
        dict2[student] = dict(dict1)
   
def read_json_update_students(students):
    try:
        if(os.path.isfile('Arvostellut.json')):
            f = open('Arvostellut.json', encoding = 'utf-8')
            arvostellut = json.load(f)
            students = arvostellut
            print("STUDENTS LISTA OHJELMAN ALUKSI ON NYT: ", students)
    except Exception:
        print("File open failed.")
        pass
    return students

def main():
    virhelista = {}
    virheen_lukumaara = 0   
    students = {} 
    virhepisteet = 0
    index = 0
    virhekoodi = []
    add_files_in_folder('', starting_path)
    list = initiate_problem_list()
    students = read_json_update_students(students)
    window = sg.Window('Grading tool', layout, resizable=True,font = font, finalize = True)
    
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
                virhelista[values['virhe']] = virheen_lukumaara
                print(virhelista[values['virhe']])
        
        ### Adding to problem counter ###
        if event == '+' or event == '-':
            if event=='+':
                try:
                    if values['-TREE-'][0] in virhelista.keys():
                        virhelista[values['-TREE-'][0]] = virhelista[values['-TREE-'][0]] + 1
                    else:
                        virheen_lukumaara = 1
                        virhelista[values['-TREE-'][0]] = virheen_lukumaara
                    window['-TREE-'].update(key = values['-TREE-'][0], value = virhelista[values['-TREE-'][0]])
                    if students:
                        for student in students:
                            if values['-TREE-'][0] in students[student] and student == path2:

                                if students[student][values['-TREE-'][0]] > 0:
                                    students[student][values['-TREE-'][0]] = students[student][values['-TREE-'][0]] + 1
                                    print("TÄÄ TULEE plus STUDENTS",students[student],  students[student][values['-TREE-'][0]])
                                    window['-TREE-'].update(key = values['-TREE-'][0], value = students[student][values['-TREE-'][0]])
                    
                except IndexError:
                    print("Listalla ei ole vielä opiskelijaa.")
                    continue
               
          ### Decreasing problem counter ###      
            if event== '-':
                if students:
                    for student in students:
                        if values['-TREE-'][0] in students[student] and student == path2:

                            if students[student][values['-TREE-'][0]] > 0:
                                students[student][values['-TREE-'][0]] = students[student][values['-TREE-'][0]] - 1
                                print("TÄÄ TULEE MIINUS STUDENTS",students[student],  students[student][values['-TREE-'][0]])
                                window['-TREE-'].update(key = values['-TREE-'][0], value = students[student][values['-TREE-'][0]])
                
                if values['-TREE-'][0] in virhelista:
                    if virhelista[values['-TREE-'][0]] >0:
                        if values['-TREE-'][0] in virhelista.keys():
                            virhelista[values['-TREE-'][0]] = virhelista[values['-TREE-'][0]] - 1
                    else:
                        virheen_lukumaara = 0
                        virhelista[values['-TREE-'][0]] = virheen_lukumaara
                    window['-TREE-'].update(key = values['-TREE-'][0], value = virhelista[values['-TREE-'][0]])
                
       #WIP: Alternative added exclude still not.
       ### List has alternatives now check if exist in virhelista and take biggest
        if  event == 'Laske virhepisteet':
            alternative_added = False
            for virhe in list:
               
                if virhe.virhe in virhelista.keys():
                    print("Listalla virheiden lukumäärä: ", virhe.lukumaara, "Virheen vakavuus: ", virhe.vakavuus)
                    print(virhelista[values['-TREE-'][0]])
                    if virhe.alternative:
                        for j in virhe.alternative:
                            for alternative in list:
                                if j == alternative.virhe:
                                    lukumaara = str(virhelista[virhe.virhe] )
                                    max_original_points = max(virhe.vakavuus.values())
                                    max_new_points = max(alternative.vakavuus.values())
                                    if lukumaara in alternative.vakavuus:
                                        virhepisteet = virhepisteet + alternative.vakavuus[lukumaara]
                                        alternative_added = True
                                        print("ALTERNATIVE VIRHEPISTEET: ", virhepisteet)
                                    
                                    elif max_original_points > max_new_points:
                                        virhepisteet = virhepisteet + max_original_points
                                        print("Alkuperäset isommat VIRHEPISTEET: ", virhepisteet)
                                    #Also fine if mistake points are the same
                                    elif virhelista[virhe.virhe]==-1:
                                        continue
                                    else:
                                        virhepisteet = virhepisteet + max_new_points
                                        print("Uudet siommat/ sama isommat VIRHEPISTEET: ", virhepisteet)
                    
                    for i in virhe.lukumaara:
                        if i == 'All' and virhelista[virhe.virhe]==-1:
                            virhepisteet = virhepisteet + int(virhe.vakavuus[i])
                            break
                        elif i == 'All' or i == 'virhekoodi':
                            continue
                        if int(i) <= virhelista[virhe.virhe]:
                            isoin = i
                            print("NYT i on pienmpi kuin virhelistan value", isoin)
                    print(i)
                    
                    if virhelista[virhe.virhe]!=-1 and alternative_added == False:
                        print("Virheen pisteet ovat :",round(virhepisteet,1))
                        virhepisteet = virhepisteet + float(virhe.vakavuus[str(isoin)])
                    print("Virheen pisteet ovat :",round(virhepisteet,1))
                    alternative_added = False
            #Lets clear the variable for new mistake points 
            virhepisteet = 0
      
       ### All occurances are wrong ###
        if event == 'ALL':
            window['-TREE-'].update(key = values['-TREE-'][0], value = -1)
            virhelista[values['-TREE-'][0]] = -1 ## -1 is easy repsesentation for all being wrong
        ### If row selected and to dict ###
        if event == '-PROGRAMS-':
            virhekoodi.clear()
            k = key_define(tree)      
            node = studentdata.tree_dict[k]
            parent_node = studentdata.tree_dict[node.parent]
            if node.parent == '':
                continue
            
            if(values['-PROGRAMS-'][0]!= node.parent):
                path2 = values['-PROGRAMS-'][0].split('/')
                path2 = path2[len(path2)-2]
                
                    #Update values since they exist already
                for student in students:
                    if student == path2:
                        for key in treedata.tree_dict:
                            node =  treedata.tree_dict[key]
                            if key not in students[student] and node.children == []:
                                node =  treedata.tree_dict[key]
                                node.values = 0
                        for err in students[student]:
                            if err in treedata.tree_dict:
                                print(students[path2][err])
                                node =  treedata.tree_dict[err]
                                node.values = students[path2][err]
                                print(students[path2][err])
                                print("NODEN JOTA LÄPIKÄYDÄÄ if ARVOT OVAT:",node.text, node.values)
                     
                window['-TREE-'].update(values = treedata)
                
                if path2 in students:
                    if 'virhekoodi' in students[path2]:
                        window['-ERROROUT-'].update(students[path2]['virhekoodi'][0])
                        window['-LEFT-'].update(visible = False)
                        index = 0

                    else:
                        window['-ERROROUT-'].update("Syötä opiskelijalle virhekoodia, jolloin se näkyy tässä.")
                        window['-RIGHT-'].update(visible=True)
                    
                if not students:
                    students[path2] = []
                if path2 not in students:
                    students[path2] = []
            window['-TREE-'].update(values = treedata)
            if virhelista:  #check if dict exists
                virhelista.clear()

###Adding checkboxes next to student names for easier marking ###
        if event.endswith('DOUBLE'):
            double_click(tree)
                
        ### Save added rows to other tree structure ###
        if event == 'SAVE':
            try:
                if virhelista != {} and path2 not in students:
                    mergedicts(virhelista,students, path2)
                    print(students)   

                elif 'virhekoodi' in students[path2] :
                    print("Tämä tulee kun virhekoodia on annettu ",students)
                    if values['virheteksti'] != '':
                        students[path2]['virhekoodi'].append(values['virheteksti']) 
                      
                    mergedicts(virhelista,students, path2)
                    print("JOS VIRHEDKOODI IN STUDENTS: ", students)
                
                else:
                    if values['virheteksti'] != '':
                        virhekoodi.append(values['virheteksti'])
                        virhelista['virhekoodi'] = virhekoodi.copy() #Adding copy of a list so program does not override existing value due referencing
                        print("Tämä tulee kun ei ole annettu arvoa vielä: ", virhelista['virhekoodi'])
                        mergedicts(virhelista,students, path2)
                        print(students)
                        
                    else:   
                        print("Ennen mergeä: ", virhelista)
                        print("Ennen mergeä: ", students)
                        mergedicts(virhelista,students, path2)
                        print(students)
                    
                    print("Toinen merge: ", students)
                window['virheteksti'].update(value = '')
            except UnboundLocalError:
                sg.popup_ok('Valitse opiskelija ja yritä uudelleen')
                print("Valitse opiskelija ja yritä uudelleen")
                pass
    #####################Counting mistake points ##############################
            alternative_added = False
           #  laske uudet lisää studenttiin 
            
            try:
                for virhe in list:
        
                    if virhe.virhe in students[path2].keys():
                        print("Listalla virheiden lukumäärä: ", virhe.lukumaara, "Virheen vakavuus: ", virhe.vakavuus)
                        if students[path2][virhe.virhe] == 0:
                            del students[path2][virhe.virhe]
                            continue
                        if virhe.alternative:
                            for j in virhe.alternative:
                                for alternative in list:
                                    if j == alternative.virhe:
                                        lukumaara = str(students[path2][virhe.virhe] )
                                        max_original_points = max(virhe.vakavuus.values())
                                        max_new_points = max(alternative.vakavuus.values())
                                        if lukumaara in alternative.vakavuus:
                                            virhepisteet = virhepisteet + alternative.vakavuus[lukumaara]
                                            alternative_added = True
                                            print("ALTERNATIVE VIRHEPISTEET: ", virhepisteet)
                                        
                                        elif max_original_points > max_new_points:
                                            virhepisteet = virhepisteet + max_original_points
                                            print("Alkuperäset isommat VIRHEPISTEET: ", virhepisteet)
                                        #Also fine if mistake points are the same
                                        elif students[path2][virhe.virhe]==-1:
                                            continue
                                        else:
                                            virhepisteet = virhepisteet + max_new_points
                                            print("Uudet siommat/ sama isommat VIRHEPISTEET: ", virhepisteet)
                        for i in virhe.lukumaara:
                            if i == 'All' and students[path2][virhe.virhe]==-1:
                                virhepisteet = virhepisteet + int(virhe.vakavuus[i])
                                break
                            elif i == 'All' or i == 'virhekoodi':
                                continue
                            if int(i) <= students[path2][virhe.virhe]:
                                isoin = i
                                print("NYT i on pienmpi kuin virhelistan value", isoin)
                        
                        
                        if students[path2][virhe.virhe]!=-1 and alternative_added == False and students[path2][virhe.virhe]!=0:
                            virhepisteet = virhepisteet + float(virhe.vakavuus[str(isoin)])
                        print("Virheen pisteet ovat :",round(virhepisteet,1))
                        alternative_added = False
                virhepisteet = round(virhepisteet, 1)
                virhelista['virhepisteet'] = virhepisteet
                #WIP: do it you bich
                window['-virheout-'].update(virhepisteet)
            except UnboundLocalError:
                print("Laita opiskelija eka.")
                pass
            try:
                mergedicts(virhelista, students, path2)
                print("Virhepisteiden laskun jälkeen STudents ja virhelista" ,students, virhelista)
            except UnboundLocalError:
                print('Valitse Opiskelija ensin.')
            #Lets clear the variable for new mistake points 
            virhepisteet = 0
        
            #WIP: Already added mistakes not counted towards mistake points
        if event == '-RIGHT-':

                index = index + 1
                try:
                    if 'virhekoodi' in students[path2]:
                        window['-ERROROUT-'].update(students[path2]['virhekoodi'][index])
                        window['-LEFT-'].update(visible=True)
                        

                except IndexError:
                    print("List end add more error code.")
                    index = index -1 
                    print(index)
                    window['-RIGHT-'].update(visible=False)
                    pass


                
        if event == '-LEFT-':
            print(values['-ERROROUT-'])
            if 'virhekoodi' in students[path2]:
                if values['-ERROROUT-'] != students[path2]['virhekoodi'][0]:
                    index = index - 1
                    window['-ERROROUT-'].update(students[path2]['virhekoodi'][index])
                    window['-RIGHT-'].update(visible = True)
            
                
               
        if event == 'WRITE':
            try:
                with open("Arvostellut.json", "w", encoding = 'utf-8') as outfile:
                    json.dump(students, outfile, indent=4)
            except Exception as e:
                print("File opening failed with error code:",e)
           
        # Example dict structure after nesting #
        #{Opiskelija: {virhekoodi1: lkm1}, Opiskelija2: {Virhekoodi2: lkm2, virhekoodi3 : lkm3}}

main()
 

  
      

 