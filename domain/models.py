from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Product:
    id: Optional[int]
    name: str
    quantity: int
    price: float


@dataclass
class OrderItem:
    product: Product
    quantity_ordered: int
    price_at_purchase: float

    @property
    def total_cost(self) -> float:
        return self.quantity_ordered * self.price_at_purchase


@dataclass
class Order:
    id: Optional[int]
    items: List[OrderItem] = field(default_factory=list)

    def add_item(self, product: Product, quantity_to_order: int):
        if quantity_to_order <= 0:
            raise ValueError("Quantity to order must be positive")
        order_item = OrderItem(
            product=product,
            quantity_ordered=quantity_to_order,
            price_at_purchase=product.price,
        )
        self.items.append(order_item)

    @property
    def total_order_cost(self) -> float:
        return sum(item.total_cost for item in self.items)
