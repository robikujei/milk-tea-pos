"""Milk Tea and Beverage Shop POS — Stage 2: ordering."""

import secrets

from flask import Flask, abort, redirect, render_template, session, url_for

app = Flask(__name__)
# A temporary key signs each browser's cart. Restarting the app resets sessions.
app.secret_key = secrets.token_hex(32)

# Store prices as whole pesos; these fixed products do not need a database.
PRODUCTS = [
    {"id": 1, "name": "Classic Milk Tea (Regular)", "price": 59},
    {"id": 2, "name": "Wintermelon Milk Tea (Regular)", "price": 65},
    {"id": 3, "name": "Taro Milk Tea (Regular)", "price": 65},
    {"id": 4, "name": "Fruit Tea – Lychee (Regular)", "price": 55},
    {"id": 5, "name": "Brown Sugar Milk Tea (Regular)", "price": 69},
    {"id": 6, "name": "Bottled Water", "price": 20},
]


@app.route("/")
def index():
    cart = session.get("cart", {})
    items = []
    for product in PRODUCTS:
        quantity = cart.get(str(product["id"]), 0)
        if quantity > 0:
            items.append({**product, "quantity": quantity,
                          "subtotal": product["price"] * quantity})
    total = sum(item["subtotal"] for item in items)
    return render_template("index.html", products=PRODUCTS, items=items, total=total)


@app.post("/cart/<int:product_id>/<action>")
def update_cart(product_id, action):
    if not any(product["id"] == product_id for product in PRODUCTS):
        abort(404)
    if action not in ("add", "decrease", "remove"):
        abort(400)

    # Only quantities are stored; names and prices always come from PRODUCTS.
    cart = session.get("cart", {})
    key = str(product_id)
    if action == "add":
        cart[key] = cart.get(key, 0) + 1
    elif action == "decrease" and cart.get(key, 0) > 1:
        cart[key] -= 1
    else:
        cart.pop(key, None)

    session["cart"] = cart
    # Redirect after POST so refreshing the page does not repeat the action.
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
