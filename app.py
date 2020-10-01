import os
from flask import Flask, redirect, url_for, request, render_template, jsonify,json
from pymongo import MongoClient

from bson import json_util
from wtforms import Form, BooleanField, StringField, PasswordField, validators



app = Flask(__name__)

client = MongoClient(os.environ["DB_PORT_27017_TCP_ADDR"], 27017)
db = client.product
db = client.kit



@app.route("/productRegister", methods=['GET', 'POST'])
def productRegister():

    if request.method == 'POST':
        product = {
            "nome": request.form["nome"],
            "sku": request.form["sku"],
            "custo": request.form["custo"],
            "preco": request.form["preco"],
            "estoque": request.form["estoque"]
        }
        db.product.insert_one(product)
    return render_template("productRegister.html")



@app.route("/kit", methods=['GET', 'POST'])
def kit():
    _products = db.product.find()
    products = [products for products in _products]

    filter = []
    for each in products:
        if int(each["estoque"]) > 0:
            filter.append(each)

    _kits = db.kit.find()
    kits = [kits for kits in _kits]

    return render_template("createKit.html", kits=kits, products=filter)



@app.route("/deletekit", methods=['POST'])
def deletekit():
    _items = db.kit.find({"sku": request.json})
    items = [items for items in _items]
    db.kit.delete_one(items[0])
    return jsonify("ok")


@app.route("/kitRegister", methods=['POST'])
def kitRegister():

    amount = []
    sku = []

    for each in request.json[0]:
        amount.append(each[0])
        sku.append(each[1])

    _items = db.product.find({"sku": {"$in" : sku}}, {"_id":0})
    items = [items for items in _items]

    min = None
    custo = 0
    preco = 0

    for i, product in enumerate(items):
        value = int(int(product["estoque"])/amount[i])
        custo += float(product["custo"]) * amount[i]
        preco += float(product["preco"]) * amount[i]

        if (min == None):
            min = value;
        elif (value < min):
            min = value;

    for product in items:
        total = int(product["estoque"]) - min * amount[i]
        db.product.update_one(product, {"$set" : { "estoque" : total }})

    preco *= (1 - int(request.json[1][2])/100)
    if preco < 0:
        preco = 0

    kit = {
        "nome": request.json[1][0],
        "sku": request.json[1][1],
        "custo": custo,
        "preco": preco,
        "estoque": min,
        "products" : items
    }


    db.kit.insert(kit)
    return "0k"



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
