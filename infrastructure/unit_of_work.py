from domain.unit_of_work import UnitOfWork
from sqlalchemy.orm import sessionmaker, Session
from .repositories import SqlAlchemyOrderRepository, SqlAlchemyProductRepository

class SqlAlchemyUnitOfWork(UnitOfWork):

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session: Session = self.session_factory()
        self.products = SqlAlchemyProductRepository(self.session)
        self.orders = SqlAlchemyOrderRepository(self.session)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()


    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
