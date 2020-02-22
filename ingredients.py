from bs4 import BeautifulSoup
import urllib.parse
import urllib.request
import re
import random
import requests

sample_url = "https://www.allrecipes.com/recipe/277917/slow-cooker-cheesy-cauliflower-casserole/"

def splitUnit(string):
    for idx in range(len(string)):
        if not string[idx].isnumeric() and string[idx] != "." and string[idx] != "/":
            return string[:idx], string[idx:]

def meatToVege(meat):
    randnum = random.randint(2, 4)

    tofus = ["soft", "medium", "firm", "extra-firm", "super-firm", "loaf", "silken"]
    mushrooms = ["white button", "crimini", "portobello", "shiitake", "oyster", "enoki", "chanterelle", "porcini", "shimeji", "morel"]
    roots = ["taro", "sweet potato", "eggplant", "zucchini"]

    if "broth" in meat:
        return "vegetable broth"
    if "cream" in meat and ("chicken" in meat or "beef" in meat):
        return "cream"

    for food in ["chicken", "beef", "bacon", "ham", "shrimp", "scallops", "clams", "mussels", "crab", "cod", "turkey", "fish", "lamb", "salmon", "tuna", "pot roast", "mahi"]:
        if food in meat:
            if randnum == 2: return random.choice(tofus) + " tofu"
            if randnum == 3: return random.choice(mushrooms) + " mushroom"
            if randnum == 4: return random.choice(roots)
    
    return meat

def VegeToMeat():
    return random.choice([
        "chicken", "beef", "bacon", "ham", "shrimp", "scallops", "clams", "mussels", "crab", "cod", "turkey", "fish", "lamb", "salmon", "tuna", "pot roast", "mahi"
    ])

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
            if typ == "toVege": delta = (1 - random.random())
            elif typ == "toMeat": delta = (1 + random.random())
            if nu in _n["nutrient-name"].lower():
                if _n.get("daily-value"):
                    _dm = float(_n["nutrient-value"]) * 100 / int(_n["daily-value"].replace("%", "").replace("<", ""))
                    _n["nutrient-value"] = str(float(_n["nutrient-value"]) * delta)
                    _n["daily-value"] = "{} %".format(int(float(_n["nutrient-value"]) * 100 / _dm))
                else:
                    _n["nutrient-value"] = str(float(_n["nutrient-value"]) * (1+random.random()))
        
        for nu in ["fiber", "vitamin", "calcium", "magnesium"]:
            if typ == "toVege": delta = (1 + random.random())
            elif typ == "toMeat": delta = (1 - random.random())
            if nu in _n["nutrient-name"].lower():
                if _n.get("daily-value"):
                    _dm = float(_n["nutrient-value"]) * 100 / int(_n["daily-value"].replace("%", "").replace("<", ""))
                    _n["nutrient-value"] = str(float(_n["nutrient-value"]) * delta)
                    _n["daily-value"] = "{} %".format(int(float(_n["nutrient-value"]) * 100 / _dm))
                else:
                    _n["nutrient-value"] = str(float(_n["nutrient-value"]) * (1+random.random()))

    return _nutritions

urls = [
    sample_url,
    "https://www.allrecipes.com/recipe/53729/fish-tacos/",
    "https://www.allrecipes.com/recipe/259473/maple-apple-turkey-sausage/",
    "https://www.allrecipes.com/recipe/50523/clarks-quiche/",
    "https://www.allrecipes.com/recipe/11758/baked-ziti-i/",
    "https://www.allrecipes.com/recipe/15925/creamy-au-gratin-potatoes/",
    "https://www.allrecipes.com/recipe/86230/szechwan-shrimp/",
    "https://www.allrecipes.com/recipe/23979/shrimp-fettuccine-alfredo/",
    "https://www.allrecipes.com/recipe/12816/cioppino/",
]

for url in urls:
    ingredients = get_ingredient(url)

    print("original", ingredients)

    _ingredients = ingredients.copy()

    for i in range(len(_ingredients)):
        _ingredients[i] = meatToVege(_ingredients[i])
    
    print("changed", _ingredients)

    nutritions = scrape_nutrition(url)
    for n in nutritions:
        print(n)
    print("")
    for n in update_nutrition(nutritions, "toVege"):
        print(n)

    print("------------------")