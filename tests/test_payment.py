"""Exercise cash validation and the complete transaction lifecycle."""

import unittest

from app import app


class PaymentTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()
        self.client.post("/cart/1/add")
        self.client.post("/cart/1/add")
        self.client.post("/cart/6/add")  # Total: 138 pesos.

    def pay(self, cash):
        return self.client.post("/pay", data={"cash": cash}, follow_redirects=True)

    def receipt(self):
        with self.client.session_transaction() as state:
            return state.get("receipt")

    def test_invalid_cash_preserves_order(self):
        cases = [
            ("", "Enter the cash received"),
            ("   ", "Enter the cash received"),
            ("abc", "Enter a valid cash amount"),
            ("-10", "cannot be negative"),
            ("0", "Insufficient cash"),
            ("137.99", "Insufficient cash"),
            ("100.001", "Enter a valid cash amount"),
            ("NaN", "Enter a valid cash amount"),
            ("Infinity", "Enter a valid cash amount"),
            ("1e3", "Enter a valid cash amount"),
            ("1,000", "Enter a valid cash amount"),
        ]
        for cash, message in cases:
            with self.subTest(cash=cash):
                response = self.pay(cash)
                self.assertEqual(response.status_code, 400)
                self.assertIn(message, response.get_data(as_text=True))
                self.assertIsNone(self.receipt())
                with self.client.session_transaction() as state:
                    self.assertEqual(state["cart"], {"1": 2, "6": 1})

    def test_exact_payment(self):
        response = self.pay("138")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.receipt()["change"], "0.00")
        self.assertIn("Payment successful!", response.get_data(as_text=True))

    def test_receipt_and_paid_order_lock(self):
        response = self.pay(" 200.50 ")
        receipt = self.receipt()
        self.assertEqual(receipt["total"], "138.00")
        self.assertEqual(receipt["cash"], "200.50")
        self.assertEqual(receipt["change"], "62.50")
        self.assertEqual(receipt["items"][0]["quantity"], 2)
        self.assertEqual(receipt["items"][0]["subtotal"], 118)
        self.assertEqual(receipt["items"][1]["subtotal"], 20)
        self.assertRegex(receipt["reference"], r"^[0-9A-F]{32}$")
        html = response.get_data(as_text=True)
        for value in ("Digital receipt", receipt["reference"], "₱200.50", "₱62.50"):
            self.assertIn(value, html)
        self.client.get("/")
        self.pay("500")
        for action in ("add", "decrease", "remove"):
            self.client.post(f"/cart/1/{action}")
        self.assertEqual(self.receipt(), receipt)
        with self.client.session_transaction() as state:
            self.assertEqual(state["cart"], {"1": 2, "6": 1})

    def test_new_transaction_and_new_reference(self):
        self.pay("200")
        old_reference = self.receipt()["reference"]
        response = self.client.post("/new-transaction", follow_redirects=True)
        html = response.get_data(as_text=True)
        self.assertIn("No items in the order", html)
        self.assertIn('id="order-total">₱0.00', html)
        self.assertIn('value=""', html)
        self.assertNotIn("Digital receipt", html)
        with self.client.session_transaction() as state:
            self.assertEqual(dict(state), {})
        self.client.post("/cart/6/add")
        self.pay("20")
        self.assertNotEqual(self.receipt()["reference"], old_reference)

    def test_empty_cart_and_missing_cash(self):
        response = self.client.post("/pay")
        self.assertEqual(response.status_code, 400)
        self.client.post("/new-transaction")
        response = self.pay("100")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Add at least one drink", response.get_data(as_text=True))
        self.assertIsNone(self.receipt())
        self.assertEqual(self.client.get("/pay").status_code, 405)
        self.assertEqual(self.client.get("/new-transaction").status_code, 405)


if __name__ == "__main__":
    unittest.main()
