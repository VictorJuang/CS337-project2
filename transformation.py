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
from ingredients import myPart

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
            print('This recipe is in ' + FOOD_TYPE['style'] + ' style.')
            return
            
    # search ingredient
    for check_word in FOOD_TYPE['style_check']:
        for ingred in recipe['ingredient']:
            if check_word in ingred:
                print('This recipe is in ' + FOOD_TYPE['style'] + ' style.')
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
        


def double_size(recipe):
    for item in recipe['nutritions']:
        print (item)
        try:
            item['nutrient-value'] = str(float(item['nutrient-value'])*2)
        except:
            print ("nutrient-value error")
        try:
            item['daily-value'] = str(float(item['daily-value'][:-2])*2)
            item['daily-value'] += " %"
        except:
            print ("daily-value error")

    def mixed_to_float(x):
        return float(sum(Fraction(term) for term in x.split()))
    count = 0
    for item in recipe['quantity']:
        print (item)
        if item.find("(") != -1:
            item = item[:item.find("(")-1]
        if item.find("/") != -1:
            item = mixed_to_float(item)
        try:
            ori = float(item)
            recipe['quantity'][count] = str(float(item)*2)
            if recipe['measure'][count] != "None" and float(recipe['quantity'][count]) > 1 and ori <= 1:
                recipe['measure'][count] += "s"
        except:
            print ("quantity error")
        count += 1
    
    for idx in recipe['steps']:
        count = 0
        for item in recipe['steps'][idx]['quantity']:
            #print (item)
            if item.find("(") != -1:
                item = item[:item.find("(")-1]
            if item.find("/") != -1:
                item = mixed_to_float(item)
            try:
                ori = float(item)
                recipe['steps'][idx]['quantity'][count] = str(float(item)*2)
                if recipe['steps'][idx]['measure'][count] != "None" and float(recipe['steps'][idx]['quantity'][count]) > 1 and ori <= 1:
                    recipe['steps'][idx]['measure'][count] += "s"
            except:
                pass
                #print ("quantity error")              
            count += 1  
        for j in range(len(recipe['detail_steps'][idx])):
            count = 0
            for item in recipe['detail_steps'][idx][j]['quantity']:
                #print (item)
                if item.find("(") != -1:
                    item = item[:item.find("(")-1]
                if item.find("/") != -1:
                    item = mixed_to_float(item)
                try:
                    ori = float(item)
                    recipe['detail_steps'][idx][j]['quantity'][count] = str(float(item)*2)
                    if recipe['detail_steps'][idx][j]['measure'][count] != "None" and float(recipe['detail_steps'][idx][j]['quantity'][count]) > 1 and ori <= 1:
                        recipe['detail_steps'][idx][j]['measure'][count] += "s"
                except:
                    pass
                    #print ("quantity error")              
                count += 1 

   
def halve_size(recipe):
    for item in recipe['nutritions']:
        print (item)
        try:
            item['nutrient-value'] = str(float(item['nutrient-value'])/2)
        except:
            print ("nutrient-value error")
        try:
            item['daily-value'] = str(float(item['daily-value'][:-2])/2)
            item['daily-value'] += " %"
        except:
            print ("daily-value error")
    def mixed_to_float(x):
        return float(sum(Fraction(term) for term in x.split()))
    count = 0
    for item in recipe['quantity']:
        print (item)
        if item.find("(") != -1:
            item = item[:item.find("(")-1]
        if item.find("/") != -1:
            item = mixed_to_float(item)
        try:
            ori = float(item)
            recipe['quantity'][count] = str(float(item)/2)
            if recipe['measure'][count] != "None" and float(recipe['quantity'][count]) > 1 and ori <= 1:
                recipe['measure'][count] += "s"
        except:
            print ("quantity error")
        count += 1
    
    for idx in recipe['steps']:
        count = 0
        for item in recipe['steps'][idx]['quantity']:
            print (item)
            if item.find("(") != -1:
                item = item[:item.find("(")-1]
            if item.find("/") != -1:
                item = mixed_to_float(item)
            try:
                ori = float(item)
                recipe['steps'][idx]['quantity'][count] = str(float(item)/2)
                if recipe['steps'][idx]['measure'][count] != "None" and float(recipe['steps'][idx]['quantity'][count]) > 1 and ori <= 1:
                    recipe['steps'][idx]['measure'][count] += "s"
            except:
                print ("quantity error")
            count += 1  
        for j in range(len(recipe['detail_steps'][idx])):
            count = 0
            for item in recipe['detail_steps'][idx][j]['quantity']:
                #print (item)
                if item.find("(") != -1:
                    item = item[:item.find("(")-1]
                if item.find("/") != -1:
                    item = mixed_to_float(item)
                try:
                    ori = float(item)
                    recipe['detail_steps'][idx][j]['quantity'][count] = str(float(item)/2)
                    if recipe['detail_steps'][idx][j]['measure'][count] != "None" and float(recipe['detail_steps'][idx][j]['quantity'][count]) > 1 and ori <= 1:
                        recipe['detail_steps'][idx][j]['measure'][count] += "s"
                except:
                    pass
                    #print ("quantity error")              
                count += 1  
   
def DIY_to_easy(ingredients, measure, quantity, descriptor, preparation, easy_magnitude, title):
    reduced_number = int (len(ingredients) * easy_magnitude)
    not_removed_ingredient = []
    for item in ingredients:
        for word in title.lower().split():
            if word in item.lower():
                not_removed_ingredient.append(item)
                break
    print ("ingredients: ", ingredients)
    print ("not_removed_ingredient", not_removed_ingredient)
    print ("reduced_number: ", reduced_number)
    print ("largest_reduced_number: ", len(ingredients) - len(not_removed_ingredient))
    if len(ingredients) - len(not_removed_ingredient) <= reduced_number:
        # remove all the other ingrdients/measure/quantity/descriptor/preparation
        can_removed_ingredient = list(set(ingredients)-set(not_removed_ingredient))
        counter = 0
        new_ingredients = []
        new_quantity = []
        new_measure = []
        new_descriptor = []
        new_preparation = []
        for item in ingredients:
            if item in not_removed_ingredient:
                new_ingredients.append(ingredients[counter])
                new_quantity.append(quantity[counter])
                new_measure.append(measure[counter])
                new_descriptor.append(descriptor[counter])
                new_preparation.append(preparation[counter])
                counter += 1
            else:
                counter += 1
                continue

        
    else:
        # raandomly remove #not_removed_ingredient
        can_removed_ingredient = list(set(ingredients) - set(not_removed_ingredient))
        counter = 0
        new_ingredients = []
        new_quantity = []
        new_measure = []
        new_descriptor = []
        new_preparation = []
        not_removed_ingredient = not_removed_ingredient + can_removed_ingredient[reduced_number:]
        for item in ingredients:
            if item in not_removed_ingredient:
                new_ingredients.append(ingredients[counter])
                new_quantity.append(quantity[counter])
                new_measure.append(measure[counter])
                new_descriptor.append(descriptor[counter])
                new_preparation.append(preparation[counter])
                counter += 1
            else:
                counter += 1
                continue
        
        
            
    return new_ingredients, new_measure, new_quantity, new_descriptor, new_preparation 

def my_part_wrapper(recipe, mode):
    _ingredients, _nutritions, _descriptor, _preparation, _measure, _quantity = \
        myPart(recipe['ingredient'], recipe['nutritions'], recipe['descriptor'], recipe['preparation'], recipe['measurement'], recipe['quantity'], mode=mode)
    #print(recipe['ingredient'])
    #print(_ingredients)
    # prepare missing ingredient
    missing_idx = []
    for ing in _ingredients:
        if ing not in recipe['ingredient']:
            missing_idx.append(_ingredients.index(ing))
            
    # apply change
    for i in range(1,len(recipe['steps'])+1):
        for idx in range(len(recipe['steps'][i]['ingredient'])):
            lookup_idx = recipe['ingredient'].index(recipe['steps'][i]['ingredient'][idx])
            if recipe['ingredient'][lookup_idx] != _ingredients[lookup_idx] or \
               recipe['descriptor'][lookup_idx] != _descriptor[lookup_idx] or \
               recipe['preparation'][lookup_idx] != _preparation[lookup_idx] or \
               recipe['measurement'][lookup_idx] != _measure[lookup_idx] or \
               recipe['quantity'][lookup_idx] != _quantity[lookup_idx]:
                recipe['steps'][i]['ingredient'][idx] = _ingredients[lookup_idx]
                recipe['steps'][i]['descriptor'][idx] = _descriptor[lookup_idx]
                recipe['steps'][i]['preparation'][idx] = _preparation[lookup_idx]
                recipe['steps'][i]['measurement'][idx] = _measure[lookup_idx]
                recipe['steps'][i]['quantity'][idx] = _quantity[lookup_idx]
        for j in range(len(recipe['detail_steps'][i])):
            for idx in range(len(recipe['detail_steps'][i][j]['ingredient'])):
                lookup_idx = recipe['ingredient'].index(recipe['detail_steps'][i][j]['ingredient'][idx])
                if recipe['ingredient'][lookup_idx] != _ingredients[lookup_idx] or \
                   recipe['descriptor'][lookup_idx] != _descriptor[lookup_idx] or \
                   recipe['preparation'][lookup_idx] != _preparation[lookup_idx] or \
                   recipe['measurement'][lookup_idx] != _measure[lookup_idx] or \
                   recipe['quantity'][lookup_idx] != _quantity[lookup_idx]:
                    recipe['detail_steps'][i][j]['ingredient'][idx] = _ingredients[lookup_idx]
                    recipe['detail_steps'][i][j]['descriptor'][idx] = _descriptor[lookup_idx]
                    recipe['detail_steps'][i][j]['preparation'][idx] = _preparation[lookup_idx]
                    recipe['detail_steps'][i][j]['measurement'][idx] = _measure[lookup_idx]
                    recipe['detail_steps'][i][j]['quantity'][idx] = _quantity[lookup_idx]
    # handle missing ingredient
    for idx in missing_idx:
        if len(recipe['steps']) > 2:
            add_step = random.choice([1,2])  
        else:
            add_step = 1
        recipe['steps'][add_step]['quantity'].append(_quantity[idx])
        recipe['steps'][add_step]['measurement'].append(_measure[idx])
        recipe['steps'][add_step]['ingredient'].append(_ingredients[idx])
        recipe['steps'][add_step]['descriptor'].append(_descriptor[idx])
        recipe['steps'][add_step]['preparation'].append(_preparation[idx])
        recipe['methods']['other'].append('add')
        recipe['steps'][add_step]['methods']['other'].append('add')
        recipe['detail_steps'][add_step][0]['quantity'].append(_quantity[idx])
        recipe['detail_steps'][add_step][0]['measurement'].append(_measure[idx])
        recipe['detail_steps'][add_step][0]['ingredient'].append(_ingredients[idx])
        recipe['detail_steps'][add_step][0]['descriptor'].append(_descriptor[idx])
        recipe['detail_steps'][add_step][0]['preparation'].append(_preparation[idx]) 
        recipe['detail_steps'][add_step][0]['methods']['other'].append('add')    
    recipe['ingredient'] = _ingredients
    recipe['nutritions'] = _nutritions
    recipe['descriptor'] = _descriptor
    recipe['preparation'] = _preparation
    recipe['measurement'] = _measure
    recipe['quantity'] = _quantity
    
def DIY_to_easy_wrapper(recipe, easy_magnitude):
    new_ingredients, new_measure, new_quantity, new_descriptor, new_preparation = \
      DIY_to_easy(recipe['ingredient'], recipe['measurement'], recipe['quantity'],\
                  recipe['descriptor'], recipe['preparation'], easy_magnitude, recipe['title'])
    
    new_ingredients_tmp = copy.deepcopy(new_ingredients)
    for i in range(1,len(recipe['steps'])+1):
        for j in range(len(recipe['detail_steps'][i])):
            for each_ing in new_ingredients_tmp:
                if each_ing in recipe['detail_steps'][i][j]['ingredient']:
                    for each_old_ing in recipe['detail_steps'][i][j]['ingredient']:
                        if each_old_ing not in new_ingredients: 
                            each_old_ing_idx = recipe['ingredient'].index(each_old_ing)
                            new_ingredients.append(each_old_ing)
                            new_measure.append(recipe['measurement'][each_old_ing_idx])
                            new_quantity.append(recipe['quantity'][each_old_ing_idx])
                            new_descriptor.append(recipe['descriptor'][each_old_ing_idx])
                            new_preparation.append(recipe['preparation'][each_old_ing_idx])
    # removable
    #print(new_ingredients)
    #print(new_ingredients_tmp)
    #print(recipe['ingredient'])
    removable = []
    for item in recipe['ingredient']:
        if item not in new_ingredients:
            removable.append(item)
    print("remove list:")
    print(removable)
    for i in range(1,len(recipe['steps'])+1):
        for item in removable:
            if item in recipe['steps'][i]['ingredient']:
                item_idx = recipe['steps'][i]['ingredient'].index(item)
                recipe['steps'][i]['ingredient'].pop(item_idx)
                recipe['steps'][i]['measurement'].pop(item_idx)
                recipe['steps'][i]['quantity'].pop(item_idx)
                recipe['steps'][i]['descriptor'].pop(item_idx)
                recipe['steps'][i]['preparation'].pop(item_idx)
        for j in range(len(recipe['detail_steps'][i])):
            for item in removable:
                if item in recipe['detail_steps'][i][j]['ingredient']:
                    item_idx = recipe['detail_steps'][i][j]['ingredient'].index(item)
                    recipe['detail_steps'][i][j]['ingredient'].pop(item_idx)
                    recipe['detail_steps'][i][j]['measurement'].pop(item_idx)
                    recipe['detail_steps'][i][j]['quantity'].pop(item_idx)
                    recipe['detail_steps'][i][j]['descriptor'].pop(item_idx)
                    recipe['detail_steps'][i][j]['preparation'].pop(item_idx)                    
    recipe['ingredient'] = new_ingredients
    recipe['quantity'] = new_quantity
    recipe['descriptor'] = new_descriptor
    recipe['preparation'] = new_preparation
    recipe['measurement'] = new_measure        