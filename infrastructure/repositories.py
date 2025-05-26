from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from domain.models import Order, Product, OrderItem
from domain.repositories import ProductRepository, OrderRepository
from .orm import ProductORM, OrderORM, OrderItemORM
import logging


class SqlAlchemyProductRepository(ProductRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, product: Product):
        product_orm = ProductORM(
            name=product.name,
            quantity=product.quantity,
            price=product.price,
        )
        self.session.add(product_orm)
        self.session.flush()
        product.id = product_orm.id

    def get(self, product_id: int) -> Product:
        product_orm = self.session.query(ProductORM).filter_by(id=product_id).one()
        return Product(
            id=product_orm.id,
            name=product_orm.name,
            quantity=product_orm.quantity,
            price=product_orm.price,
        )

    def list(self) -> List[Product]:
        products_orm = self.session.query(ProductORM).all()
        return [
            Product(id=p.id, name=p.name, quantity=p.quantity, price=p.price)
            for p in products_orm
        ]

    def update(self, product: Product):
        product_orm = (
            self.session.query(ProductORM).filter_by(id=product.id).one_or_none()
        )
        if product_orm:
            product_orm.name = product.name
            product_orm.quantity = product.quantity
            product_orm.price = product.price
        else:
            raise ValueError(f"Product with id {product.id} not found for update")


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: Session):
        self.session = session
        self.logger = logging.getLogger(__name__)

    def add(self, order: Order):
        order_orm = OrderORM()

        for domain_item in order.items:
            product_orm_ref = (
                self.session.query(ProductORM)
                .filter_by(id=domain_item.product.id)
                .one_or_none()
            )
            if not product_orm_ref:
                self.logger.error(
                    f"REPO: ProductORM with id {domain_item.product.id} not found for OrderItem."
                )
                raise ValueError(
                    f"Product (ID: {domain_item.product.id}) referenced in order item not found in DB."
                )

            item_orm = OrderItemORM(
                product_id=domain_item.product.id,
                quantity_ordered=domain_item.quantity_ordered,
                price_at_purchase=domain_item.price_at_purchase,
            )
            order_orm.items.append(item_orm)

        self.session.add(order_orm)
        self.session.flush()
        order.id = order_orm.id

        self.logger.info(
            f"REPO: Assigned order.id={order.id}. OrderORM has {len(order_orm.items)} items linked."
        )

    def get(self, order_id: int) -> Optional[Order]:
        self.logger.debug(f"REPO: Getting order with id {order_id}")

        order_orm = (
            self.session.query(OrderORM)
            .options(joinedload(OrderORM.items).joinedload(OrderItemORM.product))
            .filter_by(id=order_id)
            .one_or_none()
        )

        if order_orm:
            domain_items = []
            for item_orm in order_orm.items:
                if not item_orm.product:
                    self.logger.error(
                        f"ProductORM not loaded for orderItemORM id {item_orm.id}"
                    )
                    continue

                domain_product = Product(
                    id=item_orm.product.id,
                    name=item_orm.product.name,
                    quantity=item_orm.product.quantity,
                    price=item_orm.product.price,
                )
                domain_item = OrderItem(
                    product=domain_product,
                    quantity_ordered=item_orm.quantity_ordered,
                    price_at_purchase=item_orm.price_at_purchase,
                )
                domain_items.append(domain_item)

            return Order(id=order_orm.id, items=domain_items)
        return None

    def list(self) -> List[Order]:
        self.logger.debug("REPO: Listing all orders")
        orders_orm = (
            self.session.query(OrderORM)
            .options(joinedload(OrderORM.items).joinedload(OrderItemORM.product))
            .all()
        )

        domain_orders = []
        for order_orm in orders_orm:
            domain_items = []
            for item_orm in order_orm.items:
                if not item_orm.product:
                    self.logger.error(
                        f"REPO: ProductORM not loaded for OrderItemORM id {item_orm.id} in order id {order_orm.id}"
                    )
                    continue

                domain_product = Product(
                    id=item_orm.product.id,
                    name=item_orm.product.name,
                    quantity=item_orm.product.quantity,
                    price=item_orm.product.price,
                )
                domain_item = OrderItem(
                    product=domain_product,
                    quantity_ordered=item_orm.quantity_ordered,
                    price_at_purchase=item_orm.price_at_purchase,
                )
                domain_items.append(domain_item)
            domain_orders.append(Order(id=order_orm.id, items=domain_items))
        return domain_orders
