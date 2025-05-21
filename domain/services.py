from typing import List
from .models import Product, Order
from .unit_of_work import UnitOfWork

import logging
logger = logging.getLogger(__name__)

class WarehouseService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def create_product(self, name: str, quantity: int, price: float) -> Product:
        logger.info(f"create product with name: {name}")
        with self.uow:
            product=Product(id=None, name=name, quantity=quantity,price=price)
            self.uow.products.add(product)
            self.uow.commit()
            # self.product_repo.add(product)
            return product

    def create_order(self, product_to_add: Product) -> Order:
        logger.info(f"create order with products: {product_to_add}")
        with self.uow:
            order = Order(id=None)
            order.add_product(product_to_add)
            self.uow.orders.add(order)
            self.uow.commit()
            # self.order_repo.add(order)
            # order=Order(id=None, products=products)
            # self.order_repo.add(order)
            return order
