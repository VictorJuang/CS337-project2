from bs4 import BeautifulSoup
import urllib.parse
import urllib.request
import re
import sys
import requests
import string
from cooktool import COOK_TOOL
from methods import METHODS
from jpfood import JP_FOOD
from unimportant_words import UNIMPORTANT_WORDS

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
    title_pattern = re.compile(r'<title>[a-zA-Z\s]+')
    title = re.findall(title_pattern, str(soup))
    recipe['title'] = title[0].replace('<title>', '')[:-1]
    
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
        Descriptor.append('None')
    
    
    recipe['ingredient'] = refined_ingred
    recipe['measurement'] = measurement
    recipe['quantity'] = quantity
    recipe['descriptor'] = Descriptor
    recipe['preparation'] = Preparation
    
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
        item_tmp3_list = re.split(r'\.|;',item_tmp2[0].lower())
        #rough_direction_list.append(item_tmp2[0].translate(str.maketrans('', '', string.punctuation)).lower())
        #for subitem in item_tmp3_list:
        #    if subitem != '':
        #        direction_list.append(subitem.translate(str.maketrans('', '', string.punctuation)))
        direction_list.append(item_tmp2[0].lower())

    TIME_WORD = {
        'hours': [re.compile(r'(about )?\d+ h(ou)?rs?($|\W)'), re.compile(r'\d+ to \d+ h(ou)?rs?($|\W)')],
        'minutes': [re.compile(r'(about )?\d+ min(ute)?s?($|\W)'), re.compile(r'\d+ to \d+ min(ute)?s?($|\W)')],
        'seconds': [re.compile(r'(about )?\d+ sec(ond)?s?($|\W)'), re.compile(r'\d+ to \d+ sec(ond)?s?($|\W)')]
    }

    recipe['methods'] = {}
    recipe['methods']['primary'] = []
    recipe['methods']['other'] = []
    recipe['tools'] = []
    recipe['steps'] = {}
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
            if ingredient_count[idx] == 1:
                continue
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
            if check_word in item:
                if check_word not in recipe['methods']['other']:
                    recipe['methods']['other'].append(check_word) 
                if check_word not in recipe['steps'][count]['methods']['other']:
                    recipe['steps'][count]['methods']['other'].append(check_word)
        
        for check_type in TIME_WORD:
            for check_pattern in TIME_WORD[check_type]:
                search_res = re.search(check_pattern, item)
                if search_res:
                    recipe['steps'][count]['time'].append(search_res.group(0))
        count += 1
    
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
    
    
def japanese_style(recipe):
    # check stype
    for check_word in JP_FOOD['style_check']:
        if check_word in recipe['title']:
            print('This recipe is japanese style.')
            return
            
    # search ingredient
    for check_word in JP_FOOD['style_check']:
        if check_word in recipe['ingredient']:
            print('This recipe is japanese style.')
            return
            
def main():
    # get web info
    soup, url = fetch_url()
    recipe = parse_data(soup, url)
    
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
                print('12. Go back')
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
                    for item in recipe['steps']:
                        print(recipe['steps'][item])
                    print()
                elif sub_option == '11':
                    print('Nutritions:')
                    for item in recipe['nutritions']:
                        print(item)
                    print()
                elif sub_option == '12':
                    break
                
        elif option == "2":
            while True:
                print('Select transformation type.')
                print('1. To vegetarian ')
                print('2. From vegetarian ')
                print('3. To Japanese style')
                print('4. To Koren style')
                print('5. Easy to DIY')
                print('6. Double size')
                print('7. Half size')
                print('8. Cooking method')
                print('9. Go back')
                sub_option = input()
                
        elif option == "3":
            break             
        else:
            print('Wrong input!')
           
    
    return

if __name__ == '__main__':
    main()