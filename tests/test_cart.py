"""Check ordering behavior without starting a web server."""

import unittest

from app import app


class CartTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def change(self, product_id, action):
        return self.client.post(f"/cart/{product_id}/{action}", follow_redirects=True)

    def assert_total(self, response, total):
        self.assertEqual(response.status_code, 200)
        self.assertIn(f'id="order-total">₱{total:.2f}</strong>',
                      response.get_data(as_text=True))

    def test_ordering_sequence(self):
        self.assert_total(self.client.get("/"), 0)
        self.change(1, "add")
        response = self.change(1, "add")
        self.assert_total(response, 118)
        self.assertEqual(response.get_data(as_text=True).count('class="order-item"'), 1)
        self.assertIn('aria-label="Quantity 2"', response.get_data(as_text=True))
        self.assertIn('class="item-subtotal">₱118.00', response.get_data(as_text=True))
        self.assert_total(self.change(6, "add"), 138)
        self.assert_total(self.change(6, "add"), 158)
        self.assert_total(self.change(1, "decrease"), 99)
        self.assert_total(self.change(1, "decrease"), 40)
        response = self.change(6, "remove")
        self.assert_total(response, 0)
        self.assertIn("No items in the order", response.get_data(as_text=True))

    def test_all_products_and_refresh(self):
        for product_id in range(1, 7):
            response = self.change(product_id, "add")
        self.assert_total(response, 333)
        self.assertEqual(response.get_data(as_text=True).count('class="order-item"'), 6)
        self.assert_total(self.client.get("/"), 333)
        # Another browser must not inherit this browser's order.
        self.assert_total(app.test_client().get("/"), 0)

    def test_missing_items_and_invalid_actions(self):
        self.assert_total(self.change(1, "decrease"), 0)
        self.assert_total(self.change(1, "remove"), 0)
        self.assertEqual(self.change(999, "add").status_code, 404)
        self.assertEqual(self.change(1, "invalid").status_code, 400)
        self.assertEqual(self.client.get("/cart/1/add").status_code, 405)
        self.assert_total(self.client.get("/"), 0)


if __name__ == "__main__":
    unittest.main()
