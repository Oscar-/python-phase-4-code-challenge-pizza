#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class AllRestaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        restaurant_list = [res.to_dict(only=('address', 'id', 'name')) for res in restaurants]
        return make_response(restaurant_list, 200)

api.add_resource(AllRestaurants, '/restaurants')

class OneRestaurant(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if(not restaurant):
            return make_response({"error": "Restaurant not found"}, 404)
        return make_response(restaurant.to_dict(only=('address', 'id', 'name', 'restaurant_pizzas.id', 'restaurant_pizzas.price', 'restaurant_pizzas.pizza_id', 'restaurant_pizzas.restaurant_id', 'restaurant_pizzas.pizza.id', 'restaurant_pizzas.pizza.name', 'restaurant_pizzas.pizza.ingredients')), 200)
    
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if(not restaurant):
            return make_response({"error": "Restaurant not found"}, 404)
        db.session.delete(restaurant)
        db.session.commit()
        return make_response({}, 204)

api.add_resource(OneRestaurant, '/restaurants/<int:id>')

class AllPizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        pizza_list = [p.to_dict(only=('id', 'ingredients','name')) for p in pizzas]
        return make_response(pizza_list, 200)
    

api.add_resource(AllPizzas, '/pizzas')

class NewPizzas(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_pizza = RestaurantPizza(
                pizza_id=data.get('pizza_id'), 
                restaurant_id=data.get('restaurant_id'), 
                price=data.get('price')
            )
            db.session.add(new_pizza)
            db.session.commit()
            return make_response(new_pizza.to_dict(), 201)
    
        except:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(NewPizzas, '/restaurant_pizzas')





if __name__ == "__main__":
    app.run(port=5555, debug=True)
