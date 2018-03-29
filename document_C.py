#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re, sys

        
'''GLOBAL VARIABLES'''
#Since C allows one namespace across multiple files
function_list = {}
variable_list = {}

'''REGEX DEFINITIONS'''
'''General Use'''
clear_comments = re.compile(r'(.*)//.*')
has_slash = re.compile(r'.*\\$')
clean_line = re.compile(r'([^\\\n]*)') #nettoyer ligne pour accoler à la suiv

'''Define'''
cdef = re.compile(r'^[\t ]*#[\t ]*define[\t ]+([()….\w]+)[\t ]*([^#\\\n]*)')
is_fun = re.compile(r'^\w*[\t ]*\([\w \t,]*\)') #List func name and args

'''Include'''
incl = re.compile(r'^[\t ]*#[\t ]*include[\t ]*[<"]([^">#\n]+)')

'''Typedef'''
tdef = re.compile(r'^[\t ]*typedef[\t ]*(.*)[\t ]+(\w+)[\t ]*;$')

'''Functions'''
fdef_init = re.compile(r'^[\t ]*([^{]*)[\t ]+(\w+)[\t ]*(\(.*?\)).*;[\t ]*$')
fdef_def = re.compile(r'^[\t ]*([^{]*)[\t ]+(\w+)[\t ]*(\(.*?\)).*')

'''Variables'''
vdef = re.compile(r'^[\t ]*(\w*?)[\t ]*(\w*?)[\t ]*(\w+[\t ]*\[\w*\]|\w+)[\t ]*(?:=[\t ]*({.*}|\w+).*|;[\t ]*)')


'''SUBROUTINES'''

'''Print name of file and path if needed'''
def print_file_path(aFile) :
    path_name = re.findall('([.\w]+)', aFile)
    print "\nFile name: " + path_name[len(path_name)-1]
    if len(path_name)>1 :
        print "Path:",
        for i in range(len(path_name)-1) :
            print path_name[i]+"/"
    print ''

'''Find and print macro'''
def print_define(matched, n) :
    symbol = matched.group(1)
    definition = matched.group(2)
    global line_cont
    global m
    if definition : #if not header guard 
        #SI DEFINE EST FUNCT
        if (is_fun.match(definition)) :
            definition = func_args(definition)
        print '%04i: definition ---> %s = %s\n' % (n-m, symbol, definition)
        line_cont = None;m=0 #fin de parcours ligne cont
    else :
        print '%04i: header guards ---> %s\n' % (n-m, symbol) 
            
            
'''Create a list out of function name and arguments from define function macro'''
#Ici les macro ne listent pas les types, donc prise en charge à part de ces définitions de fonctions
def func_args(aString) :
    list_arg = re.findall('(\w+)',aString)
    definition = "function: "+list_arg[0]
    for i in range(len(list_arg)-1) :
        definition = definition+"; arg "+str(i)+": "+list_arg[i+1]
    return definition


'''Find all the functions'''
#Redondance parfois entre l'initialisation et la définition.
def find_functions(matched, n, defining) :
    fdef_n = matched.group(2)

    if fdef_n in function_list:
        function_list[fdef_n]['définition']=n-m
    else :
        function_list[fdef_n] = {}
        function_list[fdef_n]['type'] = matched.group(1)
        params_n_types = re.findall('[\( \t]?(.*?)[,\)]', matched.group(3))# Divise les paramètres

        set_parameters(params_n_types, fdef_n) #Organise paramètres 
        function_list[fdef_n]['initialisation'] = n-m
        function_list[fdef_n]['usage'] = []
        if defining :
            function_list[fdef_n]['définition']= n-m

'''Organise les paramètres d'une fonction en noms et types'''
def set_parameters(params_n_types, fdef_n):
    function_list[fdef_n]['args']=[]
    
    for i in params_n_types :
        if not i :
            function_list[fdef_n]['args']=None
            break
        params  = re.findall('(\w+[\t ]*\[\]|\w+)', i) #Divise paramètre en nom et type
        if (len(params) <= 1) :
            function_list[fdef_n]['args'].append({'name': None, 'type': params[0]})
        else :
            params_t = ''
            for y in range(len(params)-1) : #Si type + qu'un mot
                params_t = params_t + ' ' + params[y]
                
            function_list[fdef_n]['args'].append({'name': params[(len(params)-1)], 'type': params_t[1:]})

'''Trouve et divise les variables en plusieurs éléments'''
#Ici, contrairement à la fonction qui organise les éléments d'une fonction, un seul regex pour tous les cas de figure car ils se limitent à deux et sont déterministes. L'organisation en groupe, dont on vérifiera les absences ou présences, permettra d'organiser les variables globales.
def find_variables(matched, n):
    vdef_n = matched.group(3)
    variable_list[vdef_n] = {}
    variable_list[vdef_n]['type'] = matched.group(1) + ' ' + matched.group(2)
    variable_list[vdef_n]['value'] = matched.group(4)

    variable_list[vdef_n]['initialisation'] = n-m
    variable_list[vdef_n]['usage'] = []
    if matched.group(4) :
        variable_list[vdef_n]['assignment'] = n-m
    
'''Imprime en détail chaque fonction'''
def print_functions() :
    print 'Functions: \n'
    for i in function_list:
        print 'Name %s\tType: %s\nParameters:' % (i, function_list[i]['type'])
        if function_list[i]['args'] :
            c = 1
            for y in function_list[i]['args']:
                print '\tParameter %i\tName: %s\tType: %s' % (c, y['name'], y['type'])
                c = c+1
        else : print 'No Parameters'
        print 'Initialisation: %04i\tDefinition: %04i\nReferencing:\n\t' % (function_list[i]['initialisation'], function_list[i]['définition']),
        if function_list[i]['usage'] :
            for y in range(len(function_list[i]['usage'])-1) : print '%04i,' % function_list[i]['usage'][y],
            print '%04i\n' % function_list[i]['usage'][len(function_list[i]['usage'])-1]
        else : print 'No referencing\n'

'''Imprime en détail chaque variable'''
def print_variables() :
    print 'Variables: \n'
    for i in variable_list:
        print 'Name: %s\tType: %s\tValue: %s' %(i, variable_list[i]['type'], variable_list[i]['value'])
        print 'Initialisation: %04i' % variable_list[i]['initialisation'],
        if 'assignment' in variable_list[i]:
            print 'Assignment: %04i\nReferencing:\n\t' % variable_list[i]['assignment'],
        else :
            print 'Assignment: No assignment\nReferencing:\n\t',
        if variable_list[i]['usage'] :
            for y in range(len(variable_list[i]['usage'])-1) : print '%04i,' % variable_list[i]['usage'][y],
            print '%04i\n' % variable_list[i]['usage'][len(variable_list[i]['usage'])-1]
        else : print 'No referencing\n'



'''MAIN FUNCTION'''         
def scan(file) :
    print_file_path(file) #print file name and path
    global line_cont
    global m
    line_cont=None
    m=0 #if line is split
    brace_open = 0 #Start with no bracket open
    
    for n,line in enumerate(open(file)) : 
        n=n+1 #index commence à 1.
        line_tmp = clear_comments.match(line) #Get rid of double slash comments
        if line_tmp :
            line = line_tmp.group(1)
        
        if line_cont :   #si on continue une ligne préc
            #On nettoie la ligne en enlevant le slash et \n
            line = clean_line.match(line_cont).group(1) + line

        if (has_slash.match(line)) : #si slash
            line_cont=line;m=m+1 #Buffer line, augmente indic de ligne
            continue

        #Vérifie occurences de curly braces
        op_brace = re.findall('.*?({).*?', line)
        cl_brace = re.findall('.*?(}).*?', line)
        
        if not brace_open : #Si extérieur à une routine
            brace_open = len(op_brace) - len(cl_brace) #cb de routines ouvertes?

            #If define
            matched = cdef.match(line)
            if matched :
                print_define(matched, n)
                continue

            #If include
            matched = incl.match(line) #pour les include
            if matched :
                incl_file = matched.group(1)
                print '%04i: inclusion ---> %s\n' % (n-m, incl_file)
                continue

            #If typedef
            matched = tdef.match(line)
            if matched :
                tdef_type = matched.group(1)
                tdef_als = matched.group(2) 
                print '%04i: typedef ---> type: %s, alias: %s\n' % (n-m, tdef_type, tdef_als)
                continue
            
            #If function
            matched = fdef_init.match(line)
            if  matched :
                find_functions(matched, n, False)
                continue
            matched = fdef_def.match(line)
            if matched :
                find_functions(matched, n, True)
                continue

            matched = vdef.match(line)
            if matched :
                find_variables(matched, n)

        else : #Si curly braces toujours ouvert
            brace_open = brace_open + len(op_brace)-len(cl_brace)
            for i in re.split('\W+', line) : #Divise par ponctuation pour trouver nom
                if i in function_list:
                    function_list[i]['usage'].append(n-m)
                elif i in variable_list: variable_list[i]['usage'].append(n-m)
 
    print_functions()
    print_variables()

    
if len(sys.argv) is 1 :
    exit('missing source-file name')
for f in sys.argv[1:] :
    scan(f)
