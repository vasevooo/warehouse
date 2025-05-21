from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from domain.services import WarehouseService
from infrastructure.orm import Base
from infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from infrastructure.database import DATABASE_URL

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL)
SessionFactory=sessionmaker(bind=engine, autoflush=False)
Base.metadata.create_all(engine)

def main():
    uow_instance = SqlAlchemyUnitOfWork(SessionFactory)
    warehouse_service = WarehouseService(uow=uow_instance)

    product1 = warehouse_service.create_product(name="Laptop SuperX", quantity=10, price=1200.00)
    product2 = warehouse_service.create_product(name="Mouse OptiClick", quantity=5, price=25.00) 
    product3 = warehouse_service.create_product(name="Keyboard MechType", quantity=30, price=75.00)
    
    logger.info(f"P1: {product1}, P2: {product2}, P3: {product3}")

    # Формируем детали заказа: (product_id, количество_к_заказу)
    order_details_1 = []
    if product1 and product1.id:
        order_details_1.append((product1.id, 2)) # Заказываем 2 ноутбука
    if product2 and product2.id:
        order_details_1.append((product2.id, 3)) # Заказываем 3 мыши
    
    if order_details_1:
        logger.info(f"MAIN: Attempting to create order with details: {order_details_1}")
        new_order = warehouse_service.create_order(products_to_order_details=order_details_1)
        if new_order and new_order.id:
            logger.info(f"MAIN: Successfully created order: ID={new_order.id}")
            for item in new_order.items:
                logger.info(f"  Item: {item.product.name}, Qty: {item.quantity_ordered}, Price: {item.price_at_purchase}, ItemTotal: {item.total_cost}")
            logger.info(f"  Order Total: {new_order.total_order_cost}")
            # Проверим остатки на складе
            updated_p1 = warehouse_service.uow.products.get(product1.id) # Получаем свежие данные
            updated_p2 = warehouse_service.uow.products.get(product2.id)
            logger.info(f"MAIN: Stock after order: {updated_p1.name} Qty: {updated_p1.quantity}")
            logger.info(f"MAIN: Stock after order: {updated_p2.name} Qty: {updated_p2.quantity}")
        else:
            logger.error(f"MAIN: Failed to create order. Returned: {new_order}")
    else:
        logger.warning("MAIN: No valid product details to create an order.")

    # Пример заказа, где товара не хватает
    order_details_2 = []
    if product1 and product1.id: # У product1 осталось 10-2 = 8
            order_details_2.append((product1.id, 10)) # Пытаемся заказать 10 (не хватит)
    
    if order_details_2:
        logger.info(f"MAIN: Attempting to create order expected to fail (not enough stock): {order_details_2}")
        failed_order = warehouse_service.create_order(products_to_order_details=order_details_2)
        if failed_order and failed_order.id:
                logger.error(f"MAIN: Order was created despite expected stock failure: {failed_order}")
        elif failed_order and not failed_order.items:
                logger.info(f"MAIN: Order creation correctly resulted in an empty order due to stock issues: {failed_order}")
        else:
                logger.info(f"MAIN: Order creation failed as expected or returned None/other: {failed_order}")

if __name__ == "__main__":
    main()
