import PySimpleGUI as sg # Not default library
import os
import sys
import json
from io import BytesIO
from PIL import Image, ImageDraw

#V0.1.1 added constraints to mistake calculations + fixed issues when student not chosen.
sg.theme('BlueMono')      
font = ("Arial", 11)
class Virhetiedot:
    error = "",
    severity = 0
    amount = 0
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
            v.error = i['ID']
            v.severity = i['error_values']
            v.amount = i['error_values'].keys()
            if 'alternatives' in i:
                v.alternative = i['alternatives']
            lista.append(v)
            category = i['category']
        else:
            treedata.Insert(i['category'], i['ID'], i['text'], [0])
            v = Virhetiedot()
            v.error = i['ID']
            v.severity = i['error_values']
            v.amount = i['error_values'].keys()
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
                   
                   ), 
                   sg.Multiline(key = 'virheteksti', default_text = 'Laita tähän virhekoodia.', autoscroll = True, size = (25,10)), 
                   sg.Multiline(key = "-ERROROUT-",autoscroll = True, size = (25,10), tooltip = 'Syötetty koodi näkyy tässä laatikossa.')
                   ],
                   [sg.Tree(data=treedata,
                   headings=['lkm' ],
                   auto_size_columns=True,
                   select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                   num_rows=15,
                   col0_heading = 'Ongelmat koodissa                    ',
                   col0_width = 40,
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
layout = [[sg.MenuBar(menu_def, tearoff=False),sg.Text('Opiskelijat'),  sg.Text("        " *12), 
        sg.Text('Laita virheen koodi alle.'),sg.Text('     '*2), 
        sg.pin(sg.Button("<-",  enable_events = True, key = "-LEFT-")) ,sg.Text('       '*5),
        sg.Button("->", enable_events = True, key = "-RIGHT-")],
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
    
### Nice to have function for finding selected elements key ###
def key_define(tree):
    item =  tree.Widget.selection()
    return '' if len(item) == 0 else tree.IdToKey[item[0]]

###############################################################
def double_click(tree):
    item = tree.Widget.selection()[0]
    key = tree.IdToKey[item]
    index = studentdata.tree_dict[key].values[0]
    index = (index + 1) % 2
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
    with BytesIO() as output:
        im.save(output, format="PNG")
        png = output.getvalue()
    return png

check = [icon(0), icon(1)] # Two states Ready, Unchecked

def mergedicts(dict1, dict2, student):
    if dict2[student] != []:
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
        return students 
    except Exception as e:
        print("File open failed.", e)
        pass
    

def update_fields(selected_student, students,window, virhelista, k):
    node = studentdata.tree_dict[k]
    parent_node = studentdata.tree_dict[node.parent]
    if node.parent == '':
        pass
    
    if(selected_student!= node.parent):
        
        path2 = selected_student.split('/')
        #Checking if main dir if not then take main dir
        student_path = path2[len(path2)-2]
        if student_path == 'perus' or student_path == 'tavoite' or student_path == 'minimi':
            student_path = path2[len(path2)-1]
        
        print("PATH ON " , path2)
        #Update values since they exist already#
        for student in students:
            if student == student_path:
            #Update mistakepoints on click
                if 'virhepisteet' in students[student_path]:
                    window['-virheout-'].update(students[student_path]['virhepisteet'])
                else:
                    window['-virheout-'].update(0)

                for key in treedata.tree_dict:
                    node =  treedata.tree_dict[key]
                    if key not in students[student] and node.children == []:
                        node =  treedata.tree_dict[key]
                        node.values = 0
                for err in students[student]:
                    if err in treedata.tree_dict:
                        
                        node =  treedata.tree_dict[err]
                        node.values = students[student_path][err]
                        
                        print("NODEN JOTA LÄPIKÄYDÄÄ if ARVOT OVAT:",node.text, node.values)
    window['-TREE-'].update(values = treedata)
            
    if student_path in students:
        if 'virhekoodi' in students[student_path]:
            window['-ERROROUT-'].update(students[student_path]['virhekoodi'][0])
            window['-LEFT-'].update(visible = False)
            window['-RIGHT-'].update(visible = True)
            index = 0

        else:
            window['-RIGHT-'].update(visible=True)
            window['-ERROROUT-'].update('Syötetty koodi näkyy tässä.')
        
    if not students:
        students[student_path] = []
    if student_path not in students:
        students[student_path] = []
    window['-TREE-'].update(values = treedata)
    if virhelista:  #check if dict exists
        virhelista.clear()
    return student_path 

### Lets make sure that all the category amounts are zero
def clear_sums(ikkuna, list, treedata):
    category_sum = 0
    kategoria = ''
    for error in list:
        node = treedata.tree_dict[error.error]
        parent_node = treedata.tree_dict[node.parent]
        kategoria = parent_node.text
        ikkuna['-TREE-'].update(key = kategoria, value = category_sum)
    return category_sum
    
def main():
    virhelista = {}
    virheen_lukumaara = 0   
    students = {} 
    virhepisteet = 0
    category_sum = 0
    index = 0
    virhekoodi = []
    add_files_in_folder('', starting_path)
    perustiedot = initiate_problem_list()
    students = read_json_update_students(students)
    window = sg.Window('Grading tool', layout, resizable=True,font = font, finalize = True)
    tree = window['-PROGRAMS-']         # type: sg.Tree
    tree.bind("<Double-1>", '+DOUBLE')  
    
    while True:
        event, values = window.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
    
        ### Adding to problem counter ###
        if event == '+' or event == '-':
            if event=='+':
                try:
                    selected_mistake = values['-TREE-'][0]
                    if selected_mistake in virhelista.keys():
                        virhelista[selected_mistake] += 1
                    else:
                        virheen_lukumaara = 1
                        virhelista[selected_mistake] = virheen_lukumaara
                    window['-TREE-'].update(key = selected_mistake, value = virhelista[selected_mistake])
                    if students:
                        for student in students:
                            if selected_mistake in students[student] and student == path2:
                                if students[student][selected_mistake] > 0:
                                    students[student][selected_mistake] += 1
                                    window['-TREE-'].update(key = selected_mistake, value = students[student][selected_mistake])
                except IndexError:
                    print("Listalla ei ole vielä opiskelijaa.")
                    continue
               
          ### Decreasing problem counter ###      
            if event== '-':
                if students:
                    selected_mistake = values['-TREE-'][0]
                    for student in students:
                        if selected_mistake in students[student] and student == path2:

                            if students[student][selected_mistake] > 0:
                                students[student][selected_mistake] -= 1
                                window['-TREE-'].update(key = selected_mistake, value = students[student][selected_mistake])
                if selected_mistake in virhelista:
                    if virhelista[selected_mistake] >0:
                        if selected_mistake in virhelista.keys():
                            virhelista[selected_mistake] -= 1
                    else:
                        virheen_lukumaara = 0
                        virhelista[selected_mistake] = virheen_lukumaara
                    window['-TREE-'].update(key = selected_mistake, value = virhelista[selected_mistake])
                
       ### If all occurances are wrong ###
        if event == 'ALL':
            window['-TREE-'].update(key = values['-TREE-'][0], value = -1)
            virhelista[values['-TREE-'][0]] = -1 ## -1 is easy repsesentation for all being wrong
        ### If row is selected change student that is updated ###
        
        if event == '-PROGRAMS-':
            selected_student = values['-PROGRAMS-'][0]
            print(values['-PROGRAMS-'][0])
            k = key_define(tree)
            path2 = update_fields(selected_student, students,window, virhelista, k)
            print("PATH2 update fieldsin jälkeen", path2)
            window['virheteksti'].update(value = '')
            kategoria = ''
            
            ### Lets make sure that all the category amounts are zero
            
            category_sum = clear_sums(window, perustiedot, treedata)
            ### Counting category sums ###
            selected_student = students[path2]
            if selected_student != []:
                for error in perustiedot:
                    if error.error in selected_student.keys():
                        if selected_student[error.error] == 0:
                            del students[path2][error.error]
                            continue     
                        node = treedata.tree_dict[error.error]
                        parent_node = treedata.tree_dict[node.parent]

                        if parent_node.parent == '':
                            if kategoria != parent_node.text and kategoria != '':
                                window['-TREE-'].update(key = kategoria, value = category_sum)
                                category_sum = 0  
                            kategoria = parent_node.text
                            category_sum = category_sum + abs(students[path2][error.error])
                window['-TREE-'].update(key = kategoria, value = category_sum)

###Adding checkboxes next to student names for easier marking ###
        if event.endswith('DOUBLE'):
            double_click(tree)
        
        ### Save added rows to other tree structure ###
        if event == 'SAVE':
            try:
                error_text = values['virheteksti']
                if virhelista != {} and path2 not in students:
                    print("Ennen mergeä students ", students)
                    mergedicts(virhelista,students, path2)
                       

                elif 'virhekoodi' in students[path2] :
                    
                    print("Tämä tulee kun virhekoodia on annettu ",students)
                    if error_text == 'Laita tähän virhekoodia.':
                        error_text = '' 
                    if error_text != '':
                        students[path2]['virhekoodi'].append(error_text) 
                    mergedicts(virhelista,students, path2)
                else:
                    if error_text == 'Laita tähän virhekoodia.':
                        error_text = '' 
                    if error_text != '':
                        virhekoodi.append(error_text)
                    #Adding copy of a list so program does not override existing value due referencing
                        virhelista['virhekoodi'] = virhekoodi.copy() 
                        mergedicts(virhelista,students, path2)
                          
                    else:   
                        mergedicts(virhelista,students, path2)
                        print(students)
                    
                window['virheteksti'].update(value = '')
            except UnboundLocalError:
                sg.popup_ok('Valitse opiskelija ja yritä uudelleen')
                print("Valitse opiskelija ja yritä uudelleen")
                pass
    #####################Counting mistake points ##############################
            
            ###WIP: Joku error tässä
            alternative_added = False
            try:
                kategoria = ''
              
                category_sum = clear_sums(window, perustiedot, treedata)
                
                for error in perustiedot:
                    if error.error in students[path2].keys():
                        if students[path2][error.error] == 0:
                            del students[path2][error.error]
                            continue     
                        node = treedata.tree_dict[error.error]
                        parent_node = treedata.tree_dict[node.parent]
                        
                        if parent_node.parent == '':
                            
                            if kategoria != parent_node.text and kategoria != '':
                                print("KATEGORIA ON", kategoria, parent_node.text)
                                window['-TREE-'].update(key = kategoria, value = category_sum)
                                category_sum = 0
                           
                            kategoria = parent_node.text
                            print("category_sum on " , category_sum)
                            print("Virheen kohdassa students on ", students, error.error)
                            category_sum = category_sum + abs(students[path2][error.error])
                            window['-TREE-'].update(key = kategoria, value = category_sum)
                        if error.alternative:
                            for j in error.alternative:
                                for alternative in perustiedot:
                                    if j == alternative.error:
                                        amount = str(students[path2][error.error] )
                                        max_original_points = max(error.severity.values())
                                        max_new_points = max(alternative.severity.values())
                                        if amount in alternative.severity:
                                            virhepisteet = virhepisteet + alternative.severity[amount]
                                            alternative_added = True       
                                        elif max_original_points > max_new_points:
                                            virhepisteet = virhepisteet + max_original_points
                                        #Also fine if mistake points are the same
                                        elif students[path2][error.error]==-1:
                                            continue
                                        else:
                                            virhepisteet = virhepisteet + max_new_points         
                        for i in error.amount:

                            if i == 'All' and students[path2][error.error]==-1:
                                virhepisteet = virhepisteet + int(error.severity[i])
                                break
                            elif i == 'All' or i == 'virhekoodi':
                                continue
                            
                            if int(i) <= students[path2][error.error]:
                                biggest = i
                        if students[path2][error.error]!=-1 and alternative_added == False:
                            virhepisteet = virhepisteet + float(error.severity[str(biggest)])
                            
                        print("Virheen pisteet ovat :",round(virhepisteet,1))
                        alternative_added = False
            
                virhepisteet = round(virhepisteet, 1)
                virhelista['virhepisteet'] = virhepisteet
                window['-virheout-'].update(virhepisteet)
                mergedicts(virhelista, students, path2)
                print("Virhepisteiden laskun jälkeen STudents ja virhelista" ,students, virhelista)
            except UnboundLocalError:
                print('Valitse Opiskelija ensin.')
                pass
            #Lets clear the variable for new mistake points 
            virhepisteet = 0
            
            
            #WIP: Already added mistakes not counted towards mistake points
        if event == '-RIGHT-':
            index = index + 1
            try:    
                if path2 in students: 
                    if 'virhekoodi' in students[path2]:
                        window['-ERROROUT-'].update(students[path2]['virhekoodi'][index])
                        window['-LEFT-'].update(visible=True)
            except IndexError:
                print("List end add more error code.")
                index = index -1
                pass
                
        if event == '-LEFT-':
            
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
        #{Opiskelija: {TO0100: lkm1, virhekoodi: ['def main():..], virhepisteet: 4}, 
        # Opiskelija2: {TO0101: lkm2, TO0102 : lkm3, virhepisteet : 2}}

main()
 

  
      

 