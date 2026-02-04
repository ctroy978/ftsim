"""MenuItem model for food truck menu items."""

from dataclasses import dataclass, field


@dataclass
class MenuItem:
    """Represents a menu item sold by the food truck.

    All fields are required when creating menu items.
    """

    name: str
    price: float
    health_rating: int  # 1-10 scale
    item_type: str  # "food" or "drink"
    category: str  # Food: healthy/fried/sweet/savory/snack; Drink: energy/soda/juice/water/milk/coffee
    sub_type: str  # "sweet" or "savory" - affects preference matching
    energy_boost: bool
    inventory_per_day: int
    calories: int

    # Runtime inventory tracking
    _current_inventory: int = field(default=0, repr=False)

    def __post_init__(self) -> None:
        """Initialize current inventory."""
        self._current_inventory = self.inventory_per_day

    def reset_inventory(self) -> None:
        """Reset inventory to daily maximum."""
        self._current_inventory = self.inventory_per_day

    def is_available(self) -> bool:
        """Check if item is in stock."""
        return self._current_inventory > 0

    def sell_one(self) -> bool:
        """Sell one unit. Returns True if successful, False if out of stock."""
        if self._current_inventory > 0:
            self._current_inventory -= 1
            return True
        return False

    @property
    def current_inventory(self) -> int:
        """Get current inventory level."""
        return self._current_inventory

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            "name": self.name,
            "price": self.price,
            "health_rating": self.health_rating,
            "item_type": self.item_type,
            "category": self.category,
            "sub_type": self.sub_type,
            "energy_boost": self.energy_boost,
            "inventory_per_day": self.inventory_per_day,
            "calories": self.calories,
            "current_inventory": self._current_inventory,
        }
