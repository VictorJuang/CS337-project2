# CS337-project2
# Github address
```
https://github.com/VictorJuang/CS337-project2.git
```

# Package install

Please run the following command.
```
pip install -r requirements.txt
python -m nltk.downloader punkt
```

# How to use

Please run the following command.
```
python main.py
```
After running the command, you can enter the url of recipe.

After entering the year, you can choose the action you are interested in. That is, enter the number 1 ~ 3. 
1. Query
2. Transform
3. Exit

If you enter 1, you can fetch the information you are interested in. Please enter the number 1 ~ 13. 
1. Title
2. Ingredient Names
3. Quantity
4. Measurement
5. Descriptor
6. Preparation
7. Tools
8. Primary Cooking Methods
9. Other Cooking Methods
10. Steps
11. Nutrition
12. Readable Recipe
13. Go back

If you enter 2, you can apply the transformation you are interested in. Please enter the number 1 ~ 17. If you want to see the result of transformations, you should enter 17 to leave this interface and then enter 1 to go to information interface.
1. To vegetarian
2. To vegan
3. To non-vegetarian
4. To healthy
5. From healthy
6. To Japanese style
7. To Indian style
8. To Italian style
9. To Korean style
10. To Mexican style
11. To Southern style
12. Easy to DIY
13. Double size
14. Half size
15. Change Cooking method 1
16. Change Cooking method 2
17. Go back
