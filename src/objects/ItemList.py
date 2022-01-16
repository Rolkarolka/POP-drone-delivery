from objects import Item


class ItemList:
    def __init__(self, item_list: list = None, index_list: list = None):
        self._items = {}
        if item_list is not None:
            self.from_list(item_list)
        if index_list is not None:
            self.from_index_list(index_list)

    def from_list(self, item_list):
        for i in range(len(item_list)):
            self._items[i] = Item(i, item_list[i])

    def from_index_list(self, item_list):
        for index in item_list:
            if index in self._items.keys():
                self._items[index].quantity += 1
            else:
                self._items[index] = Item(index, 1)

    def is_empty(self) -> bool:
        for item_type in self._items.keys():
            if not self._items[item_type].is_empty():
                return False
        return True

    def keys(self):
        return self._items.keys()

    def __getitem__(self, key):
        return self._items[key]

    def __str__(self):
        return str(self._items)
