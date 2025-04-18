from typing import Generic, Iterator, TypeVar

T = TypeVar("T")

class BaseCollection(Generic[T]):
    """
    A generic base class for managing a collection of items, each identified 
    by a unique string ID. This class provides common functionality for adding, 
    retrieving, iterating, and accessing items in the collection.

    Attributes:
        _items (dict): A dictionary that stores items using their unique string 
                       ID as the key and the item object as the value.

    Methods:
        add(id: str, obj: T): Adds an item to the collection, using the specified 
                              ID. Overwrites any existing item with the same ID.
        __getitem__(id: str): Allows retrieving an item by its ID.
        __iter__(): Returns an iterator for iterating over all items in the collection.
        __len__(): Returns the number of items in the collection.
        keys(): Returns a list of all item IDs in the collection.
        values(): Returns a list of all items in the collection.
        items(): Returns a list of tuples, each containing an item ID and its corresponding object.
        __contains__(id: str): Checks if an item with the given ID exists in the collection.

    Example Usage:
        collection = BaseCollection[SomeClass]()
        collection.add("item1", some_instance)
        item = collection["item1"]
        for obj in collection:
            print(obj)
        if "item1" in collection:
            print("Item exists")
    """
    
    def __init__(self) -> None:
        self._items: dict[str, T] = {}

    def add(self, id: str, obj: T) -> None:
        self._items[id] = obj

    def __getitem__(self, id: str) -> T:
        return self._items[id]

    def __iter__(self) -> Iterator[T]:
        return iter(self._items.values())

    def __len__(self) -> int:
        return len(self._items)

    def keys(self) -> list[str]:
        return list(self._items.keys())

    def values(self) -> list[T]:
        return list(self._items.values())

    def items(self) -> list[tuple[str, T]]:
        return list(self._items.items())

    def __contains__(self, id: str) -> bool:
        return id in self._items