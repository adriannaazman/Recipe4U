import sqlite3
import os

ingredients = [
    ("Milk", "Used in many recipes. Can be replaced with milk powder."),
    ("Eggs", "High in protein. Used in baking."),
    ("Flour", "Basic baking ingredient."),
    ("Sugar", "Sweetener used in many dishes."),
    ("Salt", "Essential seasoning."),
    ("Butter", "Adds richness to dishes."),
    ("Oil", "Used for frying and cooking."),
    ("Rice", "Staple grain in many cultures."),
    ("Chicken", "Common protein."),
    ("Beef", "Another protein choice."),
    ("Onion", "Base for many recipes."),
    ("Garlic", "Aromatic flavor."),
    ("Tomato", "Used in sauces and salads."),
    ("Carrot", "Used in soups and stews."),
    ("Potato", "Versatile vegetable."),
    ("Broccoli", "Healthy green veggie."),
    ("Cheese", "Dairy topping."),
    ("Milk Powder", "Milk substitute."),
    ("Yogurt", "Used in marinades."),
    ("Chili Powder", "Spicy seasoning."),
    ("Cumin", "Used in Indian cuisine."),
    ("Turmeric", "Bright yellow spice."),
    ("Coriander", "Used in curries."),
    ("Ginger", "Used in Asian dishes."),
    ("Lemon", "Adds sourness."),
    ("Vinegar", "Used for pickling."),
    ("Soy Sauce", "Asian flavoring."),
    ("Fish Sauce", "Umami booster."),
    ("Coconut Milk", "Used in Thai dishes."),
    ("Oats", "Used for breakfast."),
    ("Bread", "Basic food item."),
    ("Pasta", "Italian staple."),
    ("Tomato Paste", "Condensed tomato."),
    ("Spinach", "Leafy green."),
    ("Peas", "Sweet veggie."),
    ("Green Beans", "Crunchy veggie."),
    ("Bell Pepper", "Colorful veggie."),
    ("Mushroom", "Earthy flavor."),
    ("Corn", "Sweet grain."),
    ("Honey", "Natural sweetener."),
    ("Mustard", "Used in sauces."),
    ("Mayonnaise", "Used in sandwiches."),
    ("Ketchup", "Tomato sauce."),
    ("Cream", "Used in desserts."),
    ("Ice Cream", "Frozen dessert."),
    ("Salted Butter", "For flavor."),
    ("Unsalted Butter", "For baking."),
    ("Brown Sugar", "Rich sweetener."),
    ("Baking Powder", "Helps rising."),
    ("Baking Soda", "Leavening agent.")
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database", "ingredients.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

for name, desc in ingredients:
    cursor.execute("INSERT INTO ingredients (name, description) VALUES (?, ?)", (name, desc))

conn.commit()
conn.close()
print("✅ 50 ingredients inserted successfully!")