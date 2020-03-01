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

def splitUnit(string):
    for idx in range(len(string)):
        if not string[idx].isnumeric() and string[idx] != "." and string[idx] != "/":
            return string[:idx], string[idx:]

def scrape_nutrition(recipe_url):
    all_res = []
    page_html = requests.get(recipe_url + "/fullrecipenutrition/")
    page_graph = BeautifulSoup(page_html.content, "lxml")
    for row in page_graph.find_all("div", {"class":"nutrition-row"}):
        res = {}
        for span in row.find_all("span"):
            if span.get("class"):
                key = span.get("class")[0]
                val = span.text.split(":")[0]
                if key == "nutrient-value":
                    res[key] = splitUnit(val)[0]
                    res["nutrient-unit"] = splitUnit(val)[1]
                else:
                    res[key] = val
        all_res.append(res)
    return all_res

def parse_data(soup, url):
    # get ingredient
    ingredient_pattern = re.compile(r'itemprop="recipeIngredient">(?:(?!itemprop="recipeIngredient">|<\/span>)[\s\S])*<\/span>')
    ingredients = re.findall(ingredient_pattern, str(soup))

    # data setucture
    recipe = dict()
    
    #
    title_pattern = re.compile(r'<title>(?:(?!<title>|<\/title>)[\s\S])*<\/title>') 
    title = re.findall(title_pattern, str(soup)) 
    title = title[0].replace('<title>', '').replace(' - Allrecipes.com</title>', '')
    recipe['title'] = title
    
    # ingredient
    update_ingredient = []
    for i in range(len(ingredients)):
        update_ingredient.append(ingredients[i][28:-7])    
 
    measurement = ['package', 'packages', 'carton', 'cartons', 'slice', 'slices', 'can', 'cans', 'teaspoon', 'tablespoon', 'cup', 'ounce', 'pint', 'quart', 'gallon', 'pound', 'dash', 'pinch', 'drop', 'peck', 'smidgen', 'saltspoon', 'scruple', 'coffeespoon', 'dessertspoon', 'wineglass', 'gill', 'teacup', 'pottle', 'dram', 'teaspoons', 'tablespoons', 'cups', 'ounces', 'pints', 'quarts', 'gallons', 'pounds', 'dashes', 'pinches', 'drops', 'pecks', 'smidgens', 'saltspoons', 'scruples', 'coffeespoons', 'dessertspoons', 'wineglasses', 'gills', 'teacups', 'pottles', 'drams']

    measure = []
    ingred = []
    quantity = []
    for i in range(len(update_ingredient)):
        flag = True
        for word in update_ingredient[i].lower().split():
            if word in measurement:
                
                ing_quant = update_ingredient[i].split(' '+word+' ')
                try: 
                    ingred.append(ing_quant[1])
                except:
                    flag = True
                    break
                measure.append(word)
                quantity.append(ing_quant[0])
                flag = False
                break
        if flag:
            measure.append("None")
            num_pattern = re.compile(r'\d+\/\d+|\d+')
            quan = re.findall(num_pattern, update_ingredient[i]) # only care about the first item, quant always shows at the beginning
            if quan:
                #print (quan)
                quantity.append(quan[0])
                ingred.append(re.sub(quan[0]+' ', '', update_ingredient[i]))
            else:
                quantity.append('None')
                ingred.append(update_ingredient[i])

    Descriptor = []
    Preparation = []
    refined_ingred = []
    for item in ingred:
        ss = item.split(', ')
        if ss[0] != item:
            refined_ingred.append(ss[0])
            Preparation.append(ss[1:])
        else:
            Preparation.append('None')
            refined_ingred.append(item)
        #Descriptor.append('None')
        
    #========================================
    # further refining
    #========================================
    rerefined_ingred = []
    count = 0
    for item in refined_ingred:
        des_index = []
        for descriptor in DES_PRE['descriptor']:
            if descriptor in item.lower().split():    #item.find(descriptor) != -1:
                des_index.append(item.lower().split().index(descriptor))
        if des_index:
            max_des_index = max(des_index)
        
        pre_index = []
        for pre in DES_PRE['preparation']:
            if pre in item.lower().split(): #item.find(pre) != -1:
                pre_index.append(item.lower().split().index(pre))   
        if pre_index:
            max_pre_index = max(pre_index)
        
        if des_index and not pre_index:
            rerefined_ingred.append(' '.join(item.split()[max_des_index+1:]))
            Descriptor.append(' '.join(item.split()[:max_des_index+1]))
            Preparation[count] = Preparation[count]
        if not des_index and pre_index:
            rerefined_ingred.append(' '.join(item.split()[max_pre_index+1:]))
            Descriptor.append("None")
            if Preparation[count] == "None":
                Preparation[count] = [' '.join(item.split()[:max_pre_index+1])]
            else:
                Preparation[count].append(' '.join(item.split()[:max_pre_index+1]))
        if des_index and pre_index:
            if max_des_index > max_pre_index:
                rerefined_ingred.append(' '.join(item.split()[max_des_index+1:]))
                if Preparation[count] == "None":
                    Preparation[count] = [' '.join(item.split()[:max_pre_index+1])]
                else:
                    Preparation[count].append(' '.join(item.split()[:max_pre_index+1]))
                Descriptor.append(' '.join(item.split()[max_pre_index+1:max_des_index+1]))
            else:
                rerefined_ingred.append(' '.join(item.split()[max_pre_index+1:]))
                if Preparation[count] == "None":
                    Preparation[count] = [' '.join(item.split()[max_des_index+1:max_pre_index+1])]
                else:
                    Preparation[count].append(' '.join(item.split()[max_des_index+1:max_pre_index+1]))
                Descriptor.append(' '.join(item.split()[:max_des_index+1]))
    
        if not des_index and not pre_index:
            rerefined_ingred.append(item)
            Descriptor.append("None")
            Preparation[count] = Preparation[count]
        count += 1    
    
    recipe['ingredient'] = copy.deepcopy(rerefined_ingred)
    recipe['measurement'] = measurement
    recipe['quantity'] = quantity
    recipe['descriptor'] = copy.deepcopy(Descriptor)
    recipe['preparation'] = copy.deepcopy(Preparation)
    recipe['directions'] = []
    
    #=========================================
    # parse directions
    #=========================================
    direction_pattern = re.compile(r'<span class="recipe-directions__list--item">(?:(?!<span class="recipe-directions__list--item">|<\/span>)[\s\S])*<\/span>')
    direction = re.findall(direction_pattern, str(soup))

    direction_list = []
    rough_direction_list = []
    for item in direction:
        
        item_tmp1 = re.split("<span class=\"recipe-directions__list--item\">", item)
        item_tmp2 = re.split("\n", item_tmp1[1])
        recipe['directions'].append(item_tmp2[0].lower())
        item_tmp3_list = re.split(r'\.|;',item_tmp2[0].lower())
        #rough_direction_list.append(item_tmp2[0].translate(str.maketrans('', '', string.punctuation)).lower())
        #for subitem in item_tmp3_list:
        #    if subitem != '':
        #        direction_list.append(subitem.translate(str.maketrans('', '', string.punctuation)))
        direction_list.append(item_tmp2[0].lower())

    TIME_WORD = {
        'hours': [re.compile(r'(about |\d+ to |)\d+ h(ou)?rs?')],
        'minutes': [re.compile(r'(about |\d+ to |)\d+ min(ute)?s?')],
        'seconds': [re.compile(r'(about |\d+ to |)\d+ sec(ond)?s?')]
    }

    recipe['methods'] = {}
    recipe['methods']['primary'] = []
    recipe['methods']['other'] = []
    recipe['tools'] = []
    recipe['steps'] = {}
    recipe['detail_steps'] = {}

    count = 1
    
    ingredient_count = [0] * len(recipe['ingredient'])
    
    for item in direction_list:
        
        recipe['steps'][count] = dict()
        recipe['steps'][count]['ingredient'] = []
        recipe['steps'][count]['measurement'] = []
        recipe['steps'][count]['quantity'] = []
        recipe['steps'][count]['descriptor'] = []
        recipe['steps'][count]['preparation'] = []
        recipe['steps'][count]['methods'] = dict()
        recipe['steps'][count]['methods']['primary'] = []
        recipe['steps'][count]['methods']['other'] = []
        recipe['steps'][count]['tools'] = []
        recipe['steps'][count]['time'] = []

        for idx in range(len(recipe['ingredient'])):
            #if ingredient_count[idx] == 1:
            #   continue
            check_words = recipe['ingredient'][idx]
            check_word_list = check_words.split()
            for check_word in check_word_list:
                if check_word in UNIMPORTANT_WORDS:
                    continue
                if check_word in item:
                    recipe['steps'][count]['ingredient'].append(check_words)
                    recipe['steps'][count]['measurement'].append(recipe['measurement'][idx])
                    recipe['steps'][count]['quantity'].append(recipe['quantity'][idx])
                    recipe['steps'][count]['descriptor'].append(recipe['descriptor'][idx])
                    recipe['steps'][count]['preparation'].append(recipe['preparation'][idx])
                    ingredient_count[idx] = 1
                    break
        
        for check_word in COOK_TOOL:
            if len(re.findall(COOK_TOOL[check_word], item))> 0:
                if check_word not in recipe['tools']:
                    recipe['tools'].append(check_word)
                if check_word not in recipe['steps'][count]['tools']:
                    recipe['steps'][count]['tools'].append(check_word)
                
        for check_word in METHODS['primary']:
            if check_word in item:
                if check_word not in recipe['methods']['primary']:
                    recipe['methods']['primary'].append(check_word)
                if check_word not in recipe['steps'][count]['methods']['primary']:
                    recipe['steps'][count]['methods']['primary'].append(check_word)
            elif check_word == 'sauté' and 'saute' in item:
                if check_word not in recipe['methods']['primary']:
                    recipe['methods']['primary'].append(check_word)
                if check_word not in recipe['steps'][count]['methods']['primary']:
                    recipe['steps'][count]['methods']['primary'].append(check_word)               
                    
        for check_word in METHODS['other']:
            if 'mixture' in item  and check_word == 'mix':
                continue
            if check_word in item:
                if check_word not in recipe['methods']['other']:
                    recipe['methods']['other'].append(check_word) 
                if check_word not in recipe['steps'][count]['methods']['other']:
                    recipe['steps'][count]['methods']['other'].append(check_word)
        
        for check_type in TIME_WORD:
            for check_pattern in TIME_WORD[check_type]:
                search_group = re.finditer(check_pattern, item)
                for search_res in search_group:
                    recipe['steps'][count]['time'].append(search_res.group(0))
        count += 1
    
    count = 1    
    ingredient_count = [0] * len(recipe['ingredient'])
    
    for large_item in direction_list:
        item_sub = sent_tokenize(large_item)
        recipe['detail_steps'][count] = []
 
        for item in item_sub:
            tmp_sub_recipe = dict()

            tmp_sub_recipe['ingredient'] = []
            tmp_sub_recipe['measurement'] = []
            tmp_sub_recipe['quantity'] = []
            tmp_sub_recipe['descriptor'] = []
            tmp_sub_recipe['preparation'] = []
            tmp_sub_recipe['methods'] = dict()
            tmp_sub_recipe['methods']['primary'] = []
            tmp_sub_recipe['methods']['other'] = []
            tmp_sub_recipe['tools'] = []
            tmp_sub_recipe['time'] = []
    
            for idx in range(len(recipe['ingredient'])):
                #if ingredient_count[idx] == 1:
                #    continue
                check_words = recipe['ingredient'][idx]
                check_word_list = check_words.split()
                for check_word in check_word_list:
                    if check_word in UNIMPORTANT_WORDS:
                        continue
                    if check_word in item:
                        tmp_sub_recipe['ingredient'].append(check_words)
                        tmp_sub_recipe['measurement'].append(recipe['measurement'][idx])
                        tmp_sub_recipe['quantity'].append(recipe['quantity'][idx])
                        tmp_sub_recipe['descriptor'].append(recipe['descriptor'][idx])
                        tmp_sub_recipe['preparation'].append(recipe['preparation'][idx])
                        ingredient_count[idx] = 1
                        break
            
            for check_word in COOK_TOOL:
                if len(re.findall(COOK_TOOL[check_word], item))> 0:
                    if check_word not in recipe['tools']:
                        recipe['tools'].append(check_word)
                    if check_word not in tmp_sub_recipe['tools']:
                        tmp_sub_recipe['tools'].append(check_word)
                    
            for check_word in METHODS['primary']:
                if check_word in item:
                    if check_word not in recipe['methods']['primary']:
                        recipe['methods']['primary'].append(check_word)
                    if check_word not in tmp_sub_recipe['methods']['primary']:
                        tmp_sub_recipe['methods']['primary'].append(check_word)
                elif check_word == 'sauté' and 'saute' in item:
                    if check_word not in recipe['methods']['primary']:
                        recipe['methods']['primary'].append(check_word)
                    if check_word not in tmp_sub_recipe['methods']['primary']:
                        tmp_sub_recipe['methods']['primary'].append(check_word)               
                        
            for check_word in METHODS['other']:
                if 'mixture' in item  and check_word == 'mix':
                    continue
                if check_word in item:
                    if check_word not in recipe['methods']['other']:
                        recipe['methods']['other'].append(check_word) 
                    if check_word not in tmp_sub_recipe['methods']['other']:
                        tmp_sub_recipe['methods']['other'].append(check_word)
            
            for check_type in TIME_WORD:
                for check_pattern in TIME_WORD[check_type]:
                    search_group = re.finditer(check_pattern, item)
                    for search_res in search_group:
                        tmp_sub_recipe['time'].append(search_res.group(0))
                        
            if not tmp_sub_recipe['ingredient'] and not tmp_sub_recipe['methods'] and not tmp_sub_recipe['methods']['other']:
                continue
            recipe['detail_steps'][count].append(copy.deepcopy(tmp_sub_recipe))
        count += 1
        #print(recipe['detail_steps'])
    
    recipe['nutritions'] = scrape_nutrition(url)
    return recipe  
    
def fetch_url():
    url = ""
    soup = ""
    while soup == "":
        print("Enter URL Or enter character \"x\" to leave.")
        url = input()
        if url == "x":
            print("exit program.")
            sys.exit()
        # test URL
        if urllib.parse.urlparse(url).scheme == "":
            print('Invalid URL')
            continue        
        request = requests.get(url)
        if request.status_code != 200:
            print('Web site does not exist') 
            continue
        req = urllib.request.Request(url)
        req.add_header('Cookie', 'euConsent=true')
        html_content = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(html_content, 'html.parser')
    return soup, url
    
     