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
from transformation import change_method1, change_method2, change_style, double_size, halve_size, DIT_to_easy_wrapper, my_part_wrapper
from load_data import fetch_url, parse_data

  
def print_direction(direction_dict):
    count = 1
    for item in direction_dict:
        print('Step'+ str(count)+':')
        print(item)
        print()
        count += 1


def print_detail_step(step_dict):
    for item in step_dict:
        for i in range(len(step_dict[item])):
            if len(step_dict[item]) > 1:
                print('step' + str(item) + '-' + str(i+1) + ':')
            else:
                print('step' + str(item) + ':')
                
            print('  ingredients:')
            for ing_idx in range(len(step_dict[item][i]['ingredient'])):
                ing_str = ""
                if step_dict[item][i]['quantity'][ing_idx] != 'None':
                    ing_str += step_dict[item][i]['quantity'][ing_idx] + ' '
                if step_dict[item][i]['measurement'][ing_idx] != 'None':
                    ing_str += step_dict[item][i]['measurement'][ing_idx] + ' '
                if step_dict[item][i]['descriptor'][ing_idx] != 'None':
                    ing_str += step_dict[item][i]['descriptor'][ing_idx] + ' '
                ing_str += step_dict[item][i]['ingredient'][ing_idx]
                if step_dict[item][i]['preparation'][ing_idx] != 'None':
                    ing_str += ', '
                    for tmp_pre in step_dict[item][i]['preparation'][ing_idx]:
                        ing_str += tmp_pre + ' '
                print('    ' + ing_str)
            print('  tools:')
            for tool in step_dict[item][i]['tools']:
                print('    ' + tool)
            print('  primary methods:')
            for pm in step_dict[item][i]['methods']['primary']:
                print('    ' + pm)
            print('  other methods:')
            for om in step_dict[item][i]['methods']['other']:
                print('    ' + om)
            print('  time:')
            for time in step_dict[item][i]['time']:
                print('    ' + time)
            print()

def print_step(step_dict):
    for item in step_dict:
        print('step' + str(item) + ':')
        print('  ingredients:')
        for ing_idx in range(len(step_dict[item]['ingredient'])):
            ing_str = ""
            if step_dict[item]['quantity'][ing_idx] != 'None':
                ing_str += step_dict[item]['quantity'][ing_idx] + ' '
            if step_dict[item]['measurement'][ing_idx] != 'None':
                ing_str += step_dict[item]['measurement'][ing_idx] + ' '
            if step_dict[item]['descriptor'][ing_idx] != 'None':
                ing_str += step_dict[item]['descriptor'][ing_idx] + ' '
            ing_str += step_dict[item]['ingredient'][ing_idx]
            if step_dict[item]['preparation'][ing_idx] != 'None':
                ing_str += ', '
                for tmp_pre in step_dict[item]['preparation'][ing_idx]:
                    ing_str += tmp_pre + ' '
            print('    ' + ing_str)
        print('  tools:')
        for tool in step_dict[item]['tools']:
            print('    ' + tool)
        print('  primary methods:')
        for pm in step_dict[item]['methods']['primary']:
            print('    ' + pm)
        print('  other methods:')
        for om in step_dict[item]['methods']['other']:
            print('    ' + om)
        print('  time:')
        for time in step_dict[item]['time']:
            print('    ' + time)
        print()
  
def main():
    # get web info
    soup, url = fetch_url()
    recipe = parse_data(soup, url)
    original_recipe = copy.deepcopy(recipe)
    
    #print(data)
    while True:
        print('Enter a number below to apply one of the options below.')
        print('1. Query')
        print('2. Transform')
        print('3. Exit')
        option = input()
        
        if option == "1":
            while True:
                print('Enter a number below to query information.')
                print('1. Title')
                print('2. Ingredient Names')
                print('3. Quantity')
                print('4. Measurement')
                print('5. Descriptor')
                print('6. Preparation')
                print('7. Tools')
                print('8. Primary Cooking Methods')
                print('9. Other Cooking Methods')
                print('10. Steps')
                print('11. Nutrition')
                print('12. Readable Recipe')
                print('13. Go back')
                sub_option = input()
                
                if sub_option == '1':
                    print('Title:')
                    print(recipe['title'])
                    print()
                elif sub_option == '2':
                    print('Ingredient Names:')
                    for item in recipe['ingredient']:
                        print(item)
                    print()
                elif sub_option == '3':
                    print('Quantity:')
                    for item in recipe['quantity']:
                        print(item)
                    print()
                elif sub_option == '4':
                    print('Measurement:')
                    for item in recipe['measurement']:
                        print(item)
                    print()
                elif sub_option == '5':
                    print('Descriptor:')
                    for item in recipe['descriptor']:
                        print(item)
                    print()
                elif sub_option == '6':
                    print('Preparation:')
                    for item in recipe['preparation']:
                        print(item)
                    print()
                elif sub_option == '7':
                    print('Tools:')
                    for item in recipe['tools']:
                        print(item)
                    print()
                elif sub_option == '8':
                    print('Primary Cooking Methods:')
                    for item in recipe['methods']['primary']:
                        print(item)
                    print()
                elif sub_option == '9':
                    print('Other Cooking Methods:')
                    for item in recipe['methods']['other']:
                        print(item)
                    print()
                elif sub_option == '10':
                    print('Steps:')
                    #for item in recipe['steps']:
                    #    print('step' + str(item) + ':')
                    #    print(recipe['steps'][item])
                    print(print_step(recipe['steps']))
                    print()
                elif sub_option == '11':
                    print('Nutritions:')
                    for item in recipe['nutritions']:
                        print(item)
                    print()
                elif sub_option == '12':
                    print('Detailed Steps:')
                    print_detail_step(recipe['detail_steps'])
                    print()
                elif sub_option == '13':
                    break
                
        elif option == "2":
            while True:
                print('Select transformation type.')
                print('1. To vegetarian')
                print('2. To vegan')
                print('3. To non-vegetarian')
                print('4. To healthy')
                print('5. From healthy')
                print('6. To Japanese style')
                print('7. To Indian style')
                print('8. Easy to DIY')
                print('9. Double size')
                print('10. Half size')
                print('11. Change Cooking method 1')
                print('12. Change Cooking method 2')
                print('13. Go back')
                sub_option = input()
                if sub_option == '1':
                    my_part_wrapper(recipe, "to_vegetarian")
                elif sub_option == '2':
                    my_part_wrapper(recipe, "to_vegan")
                elif sub_option == '3':
                    my_part_wrapper(recipe, "from_vegetarian")
                elif sub_option == '4':
                    my_part_wrapper(recipe, "to_healthy")
                elif sub_option == '5':
                    my_part_wrapper(recipe, "from_healthy")
                elif sub_option == '6':
                    change_style(recipe, JP_FOOD)
                elif sub_option == '7':
                    change_style(recipe, INDIAN_FOOD)
                elif sub_option == '8':   
                    ratio_input = -1
                    while ratio_input < 1 and  ratio_input > 0:
                        print('Enter a number between 0 and 1')
                        ratio_input = input()
                    DIT_to_easy_wrapper(recipe, ratio_input)
                elif sub_option == '9':
                    double_size(recipe)
                elif sub_option == '10':
                    halve_size(recipe)
                elif sub_option == '11':
                    print('Enter a primary cooking method.')
                    print(recipe['methods']['primary'])
                    from_method = input()
                    if from_method not in recipe['methods']['primary']:
                        print('No method ' + from_method + ' found in the recipe')
                        continue
                    print('Enter a primary cooking method.')
                    print(METHODS["primary"])
                    to_method = input()
                    change_method1(recipe, from_method, to_method)
                elif sub_option == '12':
                    change_method2(recipe)
                elif sub_option == '13':
                    break
                
        elif option == "3":
            break             
        else:
            print('Wrong input!')
           
    
    return

if __name__ == '__main__':
    main()