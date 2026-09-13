import unittest
from inventory import find_item

class TestInventory(unittest.TestCase):
    def test_finds_item(self):
        items = [{"id": 1, "name": "apple"}, {"id": 2, "name": "banana"}]
        self.assertEqual(find_item(items, 2)["name"], "banana")

    def test_handles_none_items(self):
        # Guards against crashing when the caller passes no inventory
        self.assertIsNone(find_item(None, 1))

    def test_missing_id_returns_none(self):
        self.assertIsNone(find_item([{"id": 1}], 99))

if __name__ == "__main__":
    unittest.main()
