# Milk Tea and Beverage Shop POS

A simple Python and Flask application for the IT 415 practical examination.
Products are defined in code, with no database required.

## Development stages

1. **Complete:** Flask setup, readable interface, six products and prices.
2. **Complete:** Add to cart, change quantities, remove items, calculate subtotals and total.
3. **Pending approval:** Validate cash, process payment, calculate change, show receipt and transaction reference, start a new transaction.

Stage 2 supports ordering. Each button submits a Flask form and reloads the
updated order summary. Cash payment and receipts remain pending for Stage 3.

The cart is kept in Flask's signed browser session, with no database. Refreshing
keeps the current order without adding items again. Restarting the server
(including a debug reload after editing Python code) resets the temporary session
key and clears the cart. Separate browsers have separate carts; tabs in the same
browser share a cart, and refreshing a tab shows its latest state.

## Files

```text
app.py                  Flask application and fixed product list
templates/index.html    Menu and order summary layout
static/css/style.css    Application styling
requirements.txt        Python dependency
tests/test_cart.py      Ordering checks using Python unittest
```

## Run on Windows (PowerShell)

Use Python 3.9 or newer. Open PowerShell in this project folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000 in your browser. Keep the terminal running while using
the application. Press `Ctrl+C` to stop it. For later runs, only the last command
is needed. Virtual environment activation is not required.

The app uses Flask's local development server with debug mode for this exercise.

## Test Stage 1

1. Start the application and open the address above. Confirm no error page appears.
2. Verify that the page has exactly these six products:

   | Product | Price |
   | --- | ---: |
   | Classic Milk Tea (Regular) | ₱59.00 |
   | Wintermelon Milk Tea (Regular) | ₱65.00 |
   | Taro Milk Tea (Regular) | ₱65.00 |
   | Fruit Tea – Lychee (Regular) | ₱55.00 |
   | Brown Sugar Milk Tea (Regular) | ₱69.00 |
   | Bottled Water | ₱20.00 |

3. Confirm the empty order summary displays a total of ₱0.00.
4. Resize the browser window. The product cards and order summary should remain readable.
5. Refresh the page and confirm the menu still displays correctly.

## Test Stage 2

Start with an empty cart (remove any existing items).

1. Add Classic Milk Tea twice. It should appear as one row with quantity 2,
   subtotal ₱118.00, and total ₱118.00.
2. Add Bottled Water. Its quantity should be 1, subtotal ₱20.00, and the total ₱138.00.
3. Click the water's **+** button. Its quantity should become 2 and the total ₱158.00.
4. Click Classic Milk Tea's **−** button. Its quantity should become 1 and the total ₱99.00.
5. Click Classic Milk Tea's **−** again. That row should disappear and the total should be ₱40.00.
6. Click **Remove** on the water row. The empty message and total ₱0.00 should return.
7. Add each of the six drinks once. The total should be ₱333.00. Refresh and verify the order is unchanged.
8. Use Tab and Enter to operate the buttons, and resize the window to check readability.

Run automated ordering checks with:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Review and commit Stage 2 before continuing to Stage 3.
