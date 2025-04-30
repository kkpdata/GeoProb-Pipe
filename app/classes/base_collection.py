from typing import Generic, Iterator, TypeVar, Union

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
        __init__(): Initializes the collection.
        __repr__(): Returns a string representation of the collection for easy inspection.
        __getitem__(index: Union[str, int, slice]): Allows retrieving an item by its ID (str),
                                                    index (int), or slice (slice).
        __iter__(): Returns an iterator for iterating over all items in the collection.
        __len__(): Returns the number of items in the collection.
        __contains__(id: str): Checks if an item with the given ID exists in the collection.
        add(id: str, obj: T): Adds an item to the collection, using the specified 
                              ID. Overwrites any existing item with the same ID.
        keys(): Returns a list of all item IDs in the collection.
        values(): Returns a list of all items in the collection.
        items(): Returns a list of tuples, each containing an item ID and its corresponding object.
    """

    def __init__(self) -> None:
        self._items: dict[str, T] = {}

    # Magic methods
    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        lines = [f"{class_name} with {len(self)} items:"]
        
        lines.append("{")
        for k, v in self._items.items():
            lines.append(f"  {k}: {repr(v)},")
        lines.append("}")
        
        # Examples for accessing by ID, index and slice
        lines.append("\nMethods to access items:")
        lines.append(f"  By ID: {class_name}['{self[0].id}'] -> {repr(self._items[str(self[0].id)])} (NOTE: ID should be given as string!)")
        lines.append(f"  By collection index: {class_name}[0] -> {repr(self[0])}")
        if len(self) > 1:
            lines.append(f"  By slicing the collection: {class_name}[0:2] -> {repr(self[0:2])}")
        return "\n".join(lines)
    
    def __getitem__(self, index: Union[str, int, slice]) -> Union[T, list[T]]:
        if isinstance(index, int):  # Handle integer indexing
            return list(self._items.values())[index]
        elif isinstance(index, slice):  # Handle slicing
            return list(self._items.values())[index]
        elif isinstance(index, str):  # Handle string-based ID lookup
            return self._items[index]
        else:
            raise TypeError("Invalid index type")

    def __iter__(self) -> Iterator[T]:
        return iter(self._items.values())

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, id: str) -> bool:
        return id in self._items

    # Normal methods
    def add(self, id: str, obj: T) -> None:
        self._items[str(id)] = obj

    def keys(self) -> list[str]:
        return list(self._items.keys())

    def values(self) -> list[T]:
        return list(self._items.values())

    def items(self) -> list[tuple[str, T]]:
        return list(self._items.items())
