def find_item(items, item_id):
    """Find an item by id. Returns None if not found or items is None."""
     for item in items:
        if item["id"] == item_id:
            return item
    return None
