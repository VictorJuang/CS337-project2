from bs4 import BeautifulSoup
import urllib.parse
import urllib.request
import re
import random
import requests
import sys

def splitUnit(string):
    for idx in range(len(string)):
        if not string[idx].isnumeric() and string[idx] != "." and string[idx] != "/":
            return string[:idx], string[idx:]

def meatToVege(ingredient):
    randnum = random.randint(2, 4)

    tofus = ["soft", "medium", "firm", "extra-firm", "super-firm", "loaf", "silken"]
    mushrooms = ["white button", "crimini", "portobello", "shiitake", "oyster", "enoki", "chanterelle", "porcini", "shimeji", "morel"]
    roots = ["taro", "sweet potato", "eggplant", "zucchini", "potato", "lotus root", "beetroot", "cassava", "corn"]

    if "broth" in ingredient:
        return "vegetable broth"
    if "cream" in ingredient and ("chicken" in ingredient or "beef" in ingredient):
        return "cream"

    for food in ["chicken", "beef", "bacon", "ham", "shrimp", "scallops", "clams", "mussels", "crab", "cod", "turkey", "fish", "lamb", "salmon", "tuna", "pot roast", "mahi"]:
        if food in ingredient:
            if randnum == 2: return random.choice(tofus) + " tofu"
            if randnum == 3: return random.choice(mushrooms) + " mushroom"
            if randnum == 4: return random.choice(roots)
    
    return ingredient

def VegeToMeat():
    return random.choice([
        "chicken", "beef", "bacon", "ham", "shrimp", "scallops", "clams", "mussels", "crab", "cod", "turkey", "fish", "lamb", "salmon", "tuna", "pot roast", "mahi"
    ])

def toHealthy(ingredient):
    if "cheese" in ingredient or "cream" in ingredient: return "low-fat " + ingredient
    elif "butter" in ingredient or "oil" in ingredient: return "extra-virgin olive oil"
    elif "syrup" in ingredient or "sugar" in ingredient or "honey" in ingredient: return "vanilla"
    return ingredient

def toVegan(ingredient):
    if "butter" in ingredient:
        return "almond butter"

    if "honey" in ingredient:
        return "vanilla"
    
    nots = ["egg", "milk", "cream", "cheese"]
    for n in nots:
        if n in ingredient:
            return random.choice(["cashews", "coconut milk", "almond milk", "avocados"])

    return ingredient

def fromHealthy():
    num = random.randint(1, 3)
    return random.sample(["bacon", "butter", "cheese", "ham", "cream"], num)

def get_ingredient(url):
    req = urllib.request.Request(url)
    req.add_header('Cookie', 'euConsent=true')

    html_content = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(html_content, 'html.parser')

    ingredient_pattern = re.compile(r'itemprop="recipeIngredient">(?:(?!itemprop="recipeIngredient">|<\/span>)[\s\S])*<\/span>')
    ingredients = re.findall(ingredient_pattern, str(soup))

    update_ingredient = []

    for i in range(len(ingredients)):
        #print (ingredients[i])
        update_ingredient.append(ingredients[i][28:-7])

    measurement = ['slice', 'slices', 'can', 'cans', 'teaspoon', 'tablespoon', 'cup', 'ounce', 'pint', 'quart', 'gallon', 'pound', 'dash', 'pinch', 'drop', 'peck', 'smidgen', 'saltspoon', 'scruple', 'coffeespoon', 'dessertspoon', 'wineglass', 'gill', 'teacup', 'pottle', 'dram', 'teaspoons', 'tablespoons', 'cups', 'ounces', 'pints', 'quarts', 'gallons', 'pounds', 'dashes', 'pinches', 'drops', 'pecks', 'smidgens', 'saltspoons', 'scruples', 'coffeespoons', 'dessertspoons', 'wineglasses', 'gills', 'teacups', 'pottles', 'drams']

    measure = []
    ingred = []
    quantity = []
    for i in range(len(update_ingredient)):
        flag = True
        #for item in measurement:
        for word in update_ingredient[i].lower().split():
            #if item in update_ingredient[i].lower().split():
            if word in measurement:
                measure.append(word)
                ing_quant = update_ingredient[i].split(' '+word+' ')
                try: 
                    ingred.append(ing_quant[1])
                except:
                    flag = True
                    break
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
                ingred.append(update_ingredient[i])

    Descriptor = []
    Preparation = []
    refined_ingred = []
    for item in ingred:
        ss = item.split(', ')
        if ss[0] != item:
            #print (ss)
            refined_ingred.append(ss[0])
            Preparation.append(ss[1:])
        else:
            Preparation.append('None')
            refined_ingred.append(item)

    return refined_ingred

def scrape_nutrition(recipe_url):
    all_res = []
    page_html = requests.get(recipe_url + "fullrecipenutrition/")
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

def update_nutrition(nutritions, typ):
    _nutritions = nutritions.copy()
    for _n in _nutritions:
        for nu in ["fat", "cholesterol", "sodium", "potassium", "protein", "carbohydrates", "iron", "folate", "magnesium"]:
            if typ == "to_vegetarian" or typ == "to_healthy" or typ == "to_vegan": delta = (1 - random.random())
            elif typ == "from_vegetarian" or typ == "from_healthy": delta = (1 + random.random())
            if nu in _n["nutrient-name"].lower():
                if _n.get("daily-value"):
                    if int(_n["daily-value"].replace("%", "").replace("<", "")) < 1:
                        _dm = 0
                    else:
                        _dm = float(_n["nutrient-value"]) * 100 /int(_n["daily-value"].replace("%", "").replace("<", ""))
                    _n["nutrient-value"] = str(float(_n["nutrient-value"]) * delta)
                    if _dm <= 0:
                        _n["daily-value"] = "{} %".format(int(0))
                    else:
                        _n["daily-value"] = "{} %".format(int(float(_n["nutrient-value"]) * 100 / _dm))
                else:
                    _n["nutrient-value"] = str(float(_n["nutrient-value"]) * (1+random.random()))

        
        for nu in ["fiber", "vitamin", "calcium", "magnesium"]:
            if typ == "to_vegetarian" or typ == "to_healthy" or typ == "to_vegan": delta = (1 + random.random())
            elif typ == "from_vegetarian" or typ == "from_healthy": delta = (1 - random.random())
            if nu in _n["nutrient-name"].lower():
                if _n.get("daily-value"):
                    if int(_n["daily-value"].replace("%", "").replace("<", "")) < 1:
                        _dm = 0
                    else:                
                        _dm = float(_n["nutrient-value"]) * 100 / int(_n["daily-value"].replace("%", "").replace("<", ""))
                    _n["nutrient-value"] = str(float(_n["nutrient-value"]) * delta)
                    if _dm <= 0:
                        _n["daily-value"] = "{} %".format(int(0))
                    else:                    
                        _n["daily-value"] = "{} %".format(int(float(_n["nutrient-value"]) * 100 / _dm))
                else:
                    _n["nutrient-value"] = str(float(_n["nutrient-value"]) * (1+random.random()))

    return _nutritions

def myPart(ingredients, nutritions, descriptor, preparation, measure, quantity, mode="to_vegetarian"):
    _ingredients, _nutritions, _descriptor, _preparation, _measure, _quantity = ingredients.copy(), nutritions.copy(), descriptor.copy(), preparation.copy(), measure.copy(), quantity.copy()
    for i in range(len(_ingredients)):
        if mode == "to_vegetarian": 
            _ingredients[i] = meatToVege(_ingredients[i])

        elif mode == "to_healthy":
            _ingredients[i] = toHealthy(meatToVege(_ingredients[i]))

        elif mode == "to_vegan":
            _ingredients[i] = toVegan(meatToVege(_ingredients[i]))
        
        elif mode == "from_vegetarian":  
            _ingredients += [VegeToMeat()]
            _descriptor = _descriptor + ['None'] * (len(_ingredients) - len(ingredients))
            _preparation = _preparation + ['None'] * (len(_ingredients) - len(ingredients))
            _measure = _measure + ['None'] * (len(_ingredients) - len(ingredients))
            _quantity = _quantity + ['None'] * (len(_ingredients) - len(ingredients))
            break
        
        elif mode == "from_healthy":
            _ingredients += fromHealthy()
            _descriptor = _descriptor + ['None'] * (len(_ingredients) - len(ingredients))
            _preparation = _preparation + ['None'] * (len(_ingredients) - len(ingredients))
            _measure = _measure + ['None'] * (len(_ingredients) - len(ingredients))
            _quantity = _quantity + ['None'] * (len(_ingredients) - len(ingredients))
            break
    print("changed ingredients: ", _ingredients)
        
    print("changed nutrition: ")
    _nutritions = update_nutrition(_nutritions, mode)
    for n in _nutritions:
        print(n)

    return _ingredients, _nutritions, _descriptor, _preparation, _measure, _quantity

def main():
    urls = [
            #sample_url,
            "https://www.allrecipes.com/recipe/53729/fish-tacos/",
            #"https://www.allrecipes.com/recipe/259473/maple-apple-turkey-sausage/",
            #"https://www.allrecipes.com/recipe/50523/clarks-quiche/",
            "https://www.allrecipes.com/recipe/11758/baked-ziti-i/",
            "https://www.allrecipes.com/recipe/15925/creamy-au-gratin-potatoes/",
            "https://www.allrecipes.com/recipe/86230/szechwan-shrimp/",
            "https://www.allrecipes.com/recipe/23979/shrimp-fettuccine-alfredo/",
            "https://www.allrecipes.com/recipe/12816/cioppino/",
        ]
    
    try: 
        mode = sys.argv[1]
        assert(mode in ["to_vegetarian", "from_vegetarian", "to_healthy", "from_healthy", "to_vegan"])
    except: 
        print("Usage: python3 ingredients.py to_vegetarian | from_vegetarian | to_healthy | from_healthy | to_vegan")
        exit(1)
    
    for url in urls:
        ingredients = get_ingredient(url)
        nutritions = scrape_nutrition(url)
    
        print("------------------- Start of this receipe -------------------")
    
        print("original ingredients: ", ingredients)

    print("original nutrition: ")
    for n in nutritions:
        print(n)

    myPart(ingredients, nutritions, descriptor=[], preparation=[], measure=[], quantity=[], mode=mode)

    print("-------------------- End of this receipe --------------------\n")