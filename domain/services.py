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
            return product
        
    def get_product_details(self, product_id: int) -> Product | None:
        with self.uow:
            product = self.uow.products.get(product_id)
            return product
        
    def list_all_products(self) -> List[Product]:
        with self.uow:
            products = self.uow.products.list()
            return products
    
    def update_product_stock(self, product_id: id, new_q: int) -> Product | None:
        with self.uow:
            product = self.uow.products.get(product_id)
            if product:
                product.quantity = new_q
                self.uow.commit()
                return product
            return None

    def create_order(self, products_to_order_details: List[tuple[int, int]]) -> Order:
        logger.info(f"SERVICE: Creating order with product details: {products_to_order_details}")
        with self.uow:
            order = Order(id=None)

            if not products_to_order_details:
                logger.warning("Attempted to create an order with no products")
                return order
            
            for product_id, quantity_to_order in products_to_order_details:
                if quantity_to_order <= 0:
                    logger.warning(f"Invalid quantity {quantity_to_order} for product ID {product_id}. Skipping")
                    continue

                product_on_stock = self.uow.products.get(product_id)

                if not product_on_stock:
                    logger.error(f"Product with ID {product_id} not found on stock. Skipping")
                    continue

                if product_on_stock.quantity < quantity_to_order:
                    logger.warning(f"SERVICE: Not enough stock for {product_on_stock.name} (ID: {product_id}). "
                    f"Requested: {quantity_to_order}, Available: {product_on_stock.quantity}. Skipping.")
                    continue

                order.add_item(product=product_on_stock, quantity_to_order=quantity_to_order)
                logger.info(f"SERVICE: Added {quantity_to_order} of {product_on_stock.name} to order.")

                product_on_stock.quantity -= quantity_to_order
                self.uow.products.update(product_on_stock)
                logger.info(f"Updated stock for {product_on_stock.name} to {product_on_stock.quantity}")

            if not order.items:
                logger.warning("SERVICE: No items were added to the order (e.g., all out of stock or invalid).")
                return order
            
            self.uow.orders.add(order)
            self.uow.commit()
            logger.info(f"SERVICE: Order created: id={order.id}, items={[item.product.name + ' q:' + str(item.quantity_ordered) for item in order.items]}")
            return order

            
