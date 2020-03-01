from bs4 import BeautifulSoup
import urllib.parse
import urllib.request
import re
import sys
import requests
import string
import numpy as np
import random
import copy
from cooktool import COOK_TOOL
from methods import METHODS
from jpfood import JP_FOOD
from indianfood import INDIAN_FOOD
from unimportant_words import UNIMPORTANT_WORDS
from nltk.tokenize import sent_tokenize
from DES_PRE import DES_PRE
from fractions import Fraction

def change_method1(recipe, from_method, to_method):
    recipe['methods']['primary'] = [to_method if x == from_method else x for x in recipe['methods']['primary']]   

    for i in range(1,len(recipe['steps'])+1):
        recipe['steps'][i]['methods']['primary'] = [to_method if x == from_method else x for x in recipe['steps'][i]['methods']['primary']] 
        for j in range(len(recipe['detail_steps'][i])):
            recipe['detail_steps'][i][j]['methods']['primary'] = [to_method if x == from_method else x for x in recipe['steps'][i]['methods']['primary']] 

def change_method2(recipe):
    from_method = random.choice(recipe['methods']['primary'])
    method_tmp = copy.deepcopy(METHODS['primary'])
    method_tmp.remove(from_method)
    to_method = random.choice(method_tmp)
    recipe['methods']['primary'] = [to_method if x == from_method else x for x in recipe['methods']['primary']]   

    for i in range(1,len(recipe['steps'])+1):
        recipe['steps'][i]['methods']['primary'] = [to_method if x == from_method else x for x in recipe['steps'][i]['methods']['primary']]  
        for j in range(len(recipe['detail_steps'][i])):
            recipe['detail_steps'][i][j]['methods']['primary'] = [to_method if x == from_method else x for x in recipe['steps'][i]['methods']['primary']] 
            

# change food style            
def change_style(recipe, FOOD_TYPE):
    # check stype
    for check_word in FOOD_TYPE['style_check']:
        if check_word in recipe['title']:
            print('This recipe is in japanese style.')
            return
            
    # search ingredient
    for check_word in FOOD_TYPE['style_check']:
        for ingred in recipe['ingredient']:
            if check_word in ingred:
                print('This recipe is in japanese style.')
                return         
    
    # check ingredient
    found = 0
    for check_word in FOOD_TYPE['change_dict']:
        new_word = random.choice(FOOD_TYPE['change_dict'][check_word])
        for idx in range(len(recipe['ingredient'])):
            ingred = recipe['ingredient'][idx]
            if check_word in ingred:
                print("change ingredient: " + ingred + " -> "+ new_word)
                found = 1
                recipe['ingredient'][idx] = new_word
        if found == 1:
            for i in range(1,len(recipe['steps'])+1):
                for idx in range(len(recipe['steps'][i]['ingredient'])):
                    ingred = recipe['steps'][i]['ingredient'][idx]
                    if check_word in ingred:
                        old_word = recipe['steps'][i]['ingredient'][idx]
                        recipe['steps'][i]['ingredient'][idx] = new_word
                        #recipe['directions'][i-1] = re.sub('(^|\W)'+old_word+'($|\W)', ' ' + check_word + ' ', recipe['directions'][i-1])
                        #recipe['directions'][i-1] = re.sub('(^|\W)'+check_word+'($|\W)', ' ' +new_word + ' ', recipe['directions'][i-1])
                        #break
            for i in range(1,len(recipe['steps'])+1):
                for j in range(len(recipe['detail_steps'][i])):
                    for idx in range(len(recipe['detail_steps'][i][j]['ingredient'])): 
                        ingred = recipe['detail_steps'][i][j]['ingredient'][idx]
                        if check_word in ingred:
                            recipe['detail_steps'][i][j]['ingredient'][idx] = new_word

                
    # change cook method
    for idx in range(len(recipe['methods']['primary'])):
        method = recipe['methods']['primary'][idx]
        if method not in FOOD_TYPE['primary_methods']:
            new_method = random.choice(FOOD_TYPE['primary_methods'])
            recipe['methods']['primary'][idx] = new_method
            for i in range(1,len(recipe['steps'])+1):
                for nidx in range(len(recipe['steps'][i]['methods']['primary'])):
                    if recipe['steps'][i]['methods']['primary'][nidx] == method:
                        recipe['steps'][i]['methods']['primary'][nidx] = new_method
                        #recipe['directions'][i-1] = re.sub('(^|\W)'+method+'($|\W)', ' ' + new_method + ' ', recipe['directions'][i-1])
            for i in range(1,len(recipe['steps'])+1):
                for j in range(len(recipe['detail_steps'][i])):
                    for nidx in range(len(recipe['detail_steps'][i][j]['methods']['primary'])): 
                        if recipe['detail_steps'][i][j]['methods']['primary'][nidx] == method:
                            recipe['detail_steps'][i][j]['methods']['primary'][nidx] = new_method
    # add ingredient
    add_item = None
    add_item_word = None
    for check_word in FOOD_TYPE['add_item_method']:
        if check_word in recipe['methods']['other']:
            add_item = random.choice(FOOD_TYPE['add_item_ingred'])
            print("add item: " + str(add_item))
            add_item_word = check_word
            break
            
    if add_item is not None:
        recipe['quantity'].append(add_item[0])
        recipe['measurement'].append(add_item[1])
        recipe['ingredient'].append(add_item[2])
        recipe['descriptor'].append('None')
        recipe['preparation'].append('None')
        recipe['methods']['other'].append('add')
        for i in range(1,len(recipe['steps'])+1):
            if add_item_word in recipe['steps'][i]['methods']['other']:
                recipe['steps'][i]['quantity'].append(add_item[0])
                recipe['steps'][i]['measurement'].append(add_item[1])
                recipe['steps'][i]['ingredient'].append(add_item[2])
                recipe['steps'][i]['descriptor'].append('None')
                recipe['steps'][i]['preparation'].append('None') 
                recipe['steps'][i]['methods']['other'].append('add')
                #temp_list = sent_tokenize(recipe['directions'][i - 1])
                #temp_direct_len = len(recipe['directions'][i - 1])
                #for j in range(temp_direct_len):
                #    if add_item_word in temp_list[j]:
                #        temp_list.insert(j, 'add ' + add_item[2] + ';')
                #        break
                #recipe['directions'][i - 1] = ' '.join(temp_list)
                for j in range(len(recipe['detail_steps'][i])):
                    if add_item_word in recipe['detail_steps'][i][j]['methods']['other']:
                        recipe['detail_steps'][i][j]['quantity'].append(add_item[0])
                        recipe['detail_steps'][i][j]['measurement'].append(add_item[1])
                        recipe['detail_steps'][i][j]['ingredient'].append(add_item[2])
                        recipe['detail_steps'][i][j]['descriptor'].append('None')
                        recipe['detail_steps'][i][j]['preparation'].append('None') 
                        recipe['detail_steps'][i][j]['methods']['other'].append('add')
                        foundx = 1 
                        break
                break
                
    if add_item is None:
        add_item = random.choice(FOOD_TYPE['add_item_ingred'])
        print("add item - type 2: " + str(add_item))
        add_step = 1
        if len(recipe['steps']) > 2:
            add_step = random.choice([1,2])
        recipe['quantity'].append(add_item[0])
        recipe['measurement'].append(add_item[1])
        recipe['ingredient'].append(add_item[2])
        recipe['descriptor'].append('None')
        recipe['preparation'].append('None')    
        recipe['steps'][add_step]['quantity'].append(add_item[0])
        recipe['steps'][add_step]['measurement'].append(add_item[1])
        recipe['steps'][add_step]['ingredient'].append(add_item[2])
        recipe['steps'][add_step]['descriptor'].append('None')
        recipe['steps'][add_step]['preparation'].append('None')
        recipe['methods']['other'].append('add')
        recipe['steps'][add_step]['methods']['other'].append('add')
        #recipe['directions'][add_step - 1]  += 'add ' + add_item[2] + '.'
        recipe['detail_steps'][add_step][0]['quantity'].append(add_item[0])
        recipe['detail_steps'][add_step][0]['measurement'].append(add_item[1])
        recipe['detail_steps'][add_step][0]['ingredient'].append(add_item[2])
        recipe['detail_steps'][add_step][0]['descriptor'].append('None')
        recipe['detail_steps'][add_step][0]['preparation'].append('None') 
        recipe['detail_steps'][add_step][0]['methods']['other'].append('add')