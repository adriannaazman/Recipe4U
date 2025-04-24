from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")  
def home():
    ingredients = load_ingredients() 
    if request.method == "POST":
        ingredient = request.form["ingredient"]
        ingredients.append(ingredient) 
        save_ingredients(ingredients) 
    return render_template("index.html") 

if __name__ == "__main__":
    app.run()
