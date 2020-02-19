from bs4 import BeautifulSoup
import requests

def splitUnit(string):
    for idx in range(len(string)):
        if not string[idx].isnumeric() and string[idx] != "." and string[idx] != "/":
            return string[:idx], string[idx:]

class RecipeFetcher:

    search_base_url = 'https://www.allrecipes.com/search/results/?wt=%s&sort=re'

    def search_recipes(self, keywords): 
        search_url = self.search_base_url %(keywords.replace(' ','+'))

        page_html = requests.get(search_url)
        page_graph = BeautifulSoup(page_html.content, "lxml")

        return [recipe.a['href'] for recipe in\
               page_graph.find_all('div', {'class':'grid-card-image-container'})]

    def scrape_recipe(self, recipe_url):
        results = {}

        page_html = requests.get(recipe_url)
        page_graph = BeautifulSoup(page_html.content, "lxml")
        
        results['ingredients'] = list(map(lambda x:x.text.replace("\n", ""), page_graph.find_all("li", {"class":"checkList__line"})))[:-3]
        results['directions'] = list(map(lambda x:x.text.replace("\n", ""), page_graph.find_all("span", {"class":"recipe-directions__list--item"})))[:-1]
        results['nutritions'] = self.scrape_nutrition(recipe_url)

        return results

    def scrape_nutrition(self, recipe_url):
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

    
rf = RecipeFetcher()
meat_lasagna = rf.search_recipes('wellington steak')[0]

print(rf.scrape_recipe(meat_lasagna))

"""
Should return:

{'ingredients': ['12 whole wheat lasagna noodles',
  '1 pound lean ground beef',
  '2 cloves garlic, chopped',
  '1/2 teaspoon garlic powder',
  '1 teaspoon dried oregano, or to taste',
  'salt and ground black pepper to taste',
  '1 (16 ounce) package cottage cheese',
  '2 eggs',
  '1/2 cup shredded Parmesan cheese',
  '1 1/2 (25 ounce) jars tomato-basil pasta sauce',
  '2 cups shredded mozzarella cheese'],
 'directions': ['Preheat oven to 350 degrees F (175 degrees C).',
  'Fill a large pot with lightly salted water and bring to a rolling boil over high heat. Once the water is boiling, add the lasagna noodles a few at a time, and return to a boil. Cook the pasta uncovered, stirring occasionally, until the pasta has cooked through, but is still firm to the bite, about 10 minutes. Remove the noodles to a plate.',
  'Place the ground beef into a skillet over medium heat, add the garlic, garlic powder, oregano, salt, and black pepper to the skillet. Cook the meat, chopping it into small chunks as it cooks, until no longer pink, about 10 minutes. Drain excess grease.',
  'In a bowl, mix the cottage cheese, eggs, and Parmesan cheese until thoroughly combined.',
  'Place 4 noodles side by side into the bottom of a 9x13-inch baking pan; top with a layer of the tomato-basil sauce, a layer of ground beef mixture, and a layer of the cottage cheese mixture. Repeat layers twice more, ending with a layer of sauce; sprinkle top with the mozzarella cheese. Cover the dish with aluminum foil.',
  'Bake in the preheated oven until the casserole is bubbling and the cheese has melted, about 30 minutes. Remove foil and bake until cheese has begun to brown, about 10 more minutes. Allow to stand at least 10 minutes before serving.']}
"""
