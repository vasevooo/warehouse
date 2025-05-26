import argparse
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain.services import WarehouseService
from infrastructure.orm import Base
from infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from infrastructure.database import DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL)
SessionFactory = sessionmaker(bind=engine, autoflush=False)
Base.metadata.create_all(engine)


def setup_service():
    uow_instance = SqlAlchemyUnitOfWork(SessionFactory)
    return WarehouseService(uow=uow_instance)


def handle_create_product(args):
    service = setup_service()
    product = service.create_product(
        name=args.name, quantity=args.quantity, price=args.price
    )
    if product and product.id:
        logger.info(
            f"Successfully created product: ID={product.id}, Name={product.name}, Qty={product.quantity}, Price={product.price}"
        )
    else:
        logger.error("Failed to create product.")


def handle_create_order(args):
    service = setup_service()

    order_details = []
    try:
        for item_str in args.items.split(";"):
            pid_str, qty_str = item_str.split(",")
            order_details.append((int(pid_str), int(qty_str)))
    except ValueError:
        logger.error(
            "Invalid format for --items. Use 'product_id,quantity;product_id,quantity;...'. Example: '1,2;3,1'"
        )
        return

    if not order_details:
        logger.warning("No items provided for the order.")
        return

    logger.info(f"Attempting to create order with details: {order_details}")
    new_order = service.create_order(products_to_order_details=order_details)

    if new_order and new_order.items:
        logger.info(f"Successfully created order: ID={new_order.id}")
        for item in new_order.items:
            logger.info(
                f"  Item: {item.product.name}, Qty: {item.quantity_ordered}, Price: {item.price_at_purchase}, ItemTotal: {item.total_cost}"
            )
        logger.info(f"  Order Total: {new_order.total_order_cost}")
    elif new_order and not new_order.items:
        logger.warning(
            f"Order (ID potential: {new_order.id}) created but contains no items (e.g. out of stock, invalid items)."
        )
    else:
        logger.error(
            f"Failed to create order or order is empty. Service returned: {new_order}"
        )


def handle_list_products(args):
    service = setup_service()
    products = service.list_all_products()
    if products:
        logger.info("Available products:")
        for p in products:
            logger.info(
                f"  ID: {p.id}, Name: {p.name}, Quantity: {p.quantity}, Price: {p.price}"
            )
    else:
        logger.info("No products found in the warehouse.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Warehouse Management CLI")
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=True
    )

    parser_create_product = subparsers.add_parser(
        "create-product", help="Create a new product"
    )
    parser_create_product.add_argument(
        "--name", type=str, required=True, help="Name of the product"
    )
    parser_create_product.add_argument(
        "--quantity", type=int, required=True, help="Initial quantity"
    )
    parser_create_product.add_argument(
        "--price", type=float, required=True, help="Price of the product"
    )
    parser_create_product.set_defaults(func=handle_create_product)

    parser_create_order = subparsers.add_parser(
        "create-order", help="Create a new order. Items format: 'id1,qty1;id2,qty2'"
    )
    parser_create_order.add_argument(
        "--items",
        type=str,
        required=True,
        help="Product items to order, format: 'product_id,quantity;product_id,quantity;...' (e.g., '1,2;3,1')",
    )
    parser_create_order.set_defaults(func=handle_create_order)

    parser_list_products = subparsers.add_parser(
        "list-products", help="List all available products"
    )
    parser_list_products.set_defaults(func=handle_list_products)

    args = parser.parse_args()
    args.func(args)
