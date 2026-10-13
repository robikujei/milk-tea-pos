"""Milk Tea and Beverage Shop POS: ordering and cash payments."""

import re
import secrets
from decimal import Decimal
from uuid import uuid4

from flask import Flask, abort, redirect, render_template, request, session, url_for

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


def get_order():
    """Recalculate the order using the fixed product prices."""
    cart = session.get("cart", {})
    items = []
    for product in PRODUCTS:
        quantity = cart.get(str(product["id"]), 0)
        if quantity > 0:
            items.append({**product, "quantity": quantity,
                          "subtotal": product["price"] * quantity})
    total = sum(item["subtotal"] for item in items)
    return items, total


def render_pos(error=None, cash=""):
    items, total = get_order()
    return render_template("index.html", products=PRODUCTS, items=items, total=total,
                           receipt=session.get("receipt"), error=error, cash=cash)


@app.route("/")
def index():
    return render_pos()


@app.post("/cart/<int:product_id>/<action>")
def update_cart(product_id, action):
    # A paid order stays unchanged until New Transaction is selected.
    if session.get("receipt"):
        return redirect(url_for("index"))
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


@app.post("/pay")
def pay():
    # Repeated submissions must keep the same completed receipt.
    if session.get("receipt"):
        return redirect(url_for("index"))

    items, total = get_order()
    cash_text = request.form.get("cash", "").strip()
    error = None
    if not items:
        error = "Add at least one drink before processing payment."
    elif not cash_text:
        error = "Enter the cash received."
    elif cash_text.startswith("-"):
        error = "Cash received cannot be negative."
    elif not re.fullmatch(r"[0-9]{1,9}(\.[0-9]{1,2})?", cash_text):
        error = "Enter a valid cash amount using up to 9 digits and 2 decimal places (for example, 100.50)."
    else:
        # Decimal avoids floating-point rounding errors for centavos.
        cash = Decimal(cash_text)
        if cash < total:
            error = f"Insufficient cash. Enter at least ₱{total:.2f}."

    if error:
        return render_pos(error=error, cash=cash_text), 400

    session["receipt"] = {
        "reference": uuid4().hex.upper(),
        "items": items,
        "total": f"{total:.2f}",
        "cash": f"{cash:.2f}",
        "change": f"{cash - Decimal(total):.2f}",
    }
    return redirect(url_for("index"))


@app.post("/new-transaction")
def new_transaction():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
