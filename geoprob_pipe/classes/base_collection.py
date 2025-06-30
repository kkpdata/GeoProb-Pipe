from __future__ import annotations  # makes all annotations lazy (no quotes needed)

from itertools import islice
from typing import TYPE_CHECKING, Generic, Iterator, TypeVar, Union

if TYPE_CHECKING:
    from geoprob_pipe.classes.ondergrond_scenario import OndergrondScenario
    from geoprob_pipe.classes.uittredepunt import Uittredepunt
    from geoprob_pipe.classes.vak import Vak
    from geoprob_pipe.classes.overschrijdingsfrequentielijn import Overschrijdingsfrequentielijn
T = TypeVar("T")


SHOW_NUMBER_ATTRIBUTES = 2  # Defines number of attributes to show (to prevent long prints)
SHOW_NUMBER_SUBATTRIBUTES = 4  # Defines number of subattributes (i.e. attributes of attributes) to show (to prevent long prints)


def _show_limited_subattributes(instance: T) -> str:
    attrs = list(instance.__dict__.items())[:SHOW_NUMBER_SUBATTRIBUTES]
    return ", ".join(f"{ak}={repr(av)}" for ak, av in attrs)


class BaseCollection(Generic[T]):
    """
    A generic base class for managing a collection of items, each identified 
    by a unique string ID. This class provides common functionality for adding, 
    retrieving, iterating, and accessing items in the collection.

    Check the __repr__ attribute for examples regarding accessing data

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

        # Header text
        lines = [f"{self.__class__.__name__} with {len(self)} items:", "    {"]

        # Text regarding instances within collection
        for _, instance in islice(self._items.items(), SHOW_NUMBER_ATTRIBUTES):
            lines.append(f"      {instance.__class__.__name__}({_show_limited_subattributes(instance)}, ...)")
        lines.append("      ...")
        lines.append("    }")
        
        # Text with examples for accessing by ID, index and slice
        lines.append("\nMethods to access items:")
        lines.append(f"    By ID: {self.__class__.__name__}['{self[0].id}'] (NOTE: ID should be given as string!) -> {self[0].__class__.__name__}({(_show_limited_subattributes(self._items[str(self[0].id)]))}, ...)")
        lines.append(f"    By collection index: {self.__class__.__name__}[0] -> {self[0].__class__.__name__}({_show_limited_subattributes(self[0])}, ...)")
        if len(self) > 1:
            lines.append(f"    By slicing the collection: {self.__class__.__name__}[0:2] -> [" + 
                         ", ".join(
                             f"{instance.__class__.__name__}({_show_limited_subattributes(instance)}, ...)"
                             for instance in self[0:2]
                         ) + "]")
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

    def __contains__(self, identifier: str) -> bool:
        return identifier in self._items

    # Normal methods
    def add(self, identifier: str, obj: T) -> None:
        self._items[str(identifier)] = obj

    def keys(self) -> list[str]:
        return list(self._items.keys())

    def values(self) -> list[T]:
        return list(self._items.values())

    def items(self) -> list[tuple[str, T]]:
        return list(self._items.items())

def _pretty_repr(self: Vak | Uittredepunt | OndergrondScenario | Overschrijdingsfrequentielijn) -> str:
    def format_value(v, indent=2):
        spacer = '    ' * indent

        # Special case 1: Single instance of Vak/Uittredepunt/OndergrondScenario/Overschrijdingsfrequentielijn
        if type(v).__name__ in ("Vak", "Uittredepunt", "OndergrondScenario"):
            return format_instance(v, indent)

        # Special case 2: List of Uittredepunt or OndergrondScenario
        if isinstance(v, list) and v and type(v[0]).__name__ in ("Uittredepunt", "OndergrondScenario"):
            sliced = v[:2]
            body = ''.join(
                f'{spacer}{format_instance(item, indent + 1)}\n'
                for item in sliced
            )
            return '[\n' + body + f'{spacer}...]\n'

        # Regular dict
        elif isinstance(v, dict):
            return '{\n' + ''.join(
                f'{spacer}{k}: {format_value(val, indent + 1)}\n'
                for k, val in v.items()
            ) + '    ' * (indent - 1) + '}'

        # Recursively format objects with __dict__
        elif hasattr(v, '__dict__'):
            return format_value(v.__dict__, indent)

        # Fallback
        else:
            return repr(v)

    def format_instance(obj, indent=2):
        spacer = '    ' * indent
        items = list(obj.__dict__.items())[:4]
        body = ''.join(
            f'{spacer}{k}: {format_value(val, indent + 1)}\n'
            for k, val in items
        )
        return f'{obj.__class__.__name__}(\n{body}{spacer}...)\n{spacer[:-4]})'

    return (
        f"{self.__class__.__name__}(\n" +
        ''.join(f'    {k}: {format_value(v)}\n' for k, v in self.__dict__.items()) +
        ")"
    )
