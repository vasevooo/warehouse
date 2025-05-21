from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from domain.services import WarehouseService
from infrastructure.orm import Base
from infrastructure.repositories import SqlAlchemyProductRepository, SqlAlchemyOrderRepository
from infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from infrastructure.database import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionFactory=sessionmaker(bind=engine, autoflush=False)
Base.metadata.create_all(engine)

def main():
    uow = SqlAlchemyUnitOfWork(SessionFactory)

    warehouse_service = WarehouseService(uow=uow)
    new_product = warehouse_service.create_product(name="test1", quantity=1, price=100)
    print(f"create product: {new_product}")
    
    # uow.commit()
    # todo add some actions
    if new_product and new_product.id is not None:
        new_order = warehouse_service.create_order(product_to_add=new_product)
        print(f"Created order: {new_order}")
    else:
        print("Failed to create product or product ID is None")

if __name__ == "__main__":
    main()
