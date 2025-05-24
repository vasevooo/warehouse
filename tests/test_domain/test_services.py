import pytest
from domain.models import Product, Order, OrderItem
from domain.services import WarehouseService
from domain.unit_of_work import UnitOfWork
from domain.repositories import ProductRepository, OrderRepository


@pytest.fixture
def mock_uow(mocker):
    uow = mocker.MagicMock(spec=UnitOfWork)
    uow.products = mocker.MagicMock(spec=ProductRepository)
    uow.orders = mocker.MagicMock(spec=OrderRepository)
    return uow


def test_create_product_adds_and_commits(mock_uow, mocker):

    product_name = 'Test Product'
    product_q = 50
    product_p = 10.99

    service = WarehouseService(uow=mock_uow)

    created_product = service.create_product(
        name=product_name,
        quantity=product_q,
        price=product_p
    )

    assert isinstance(created_product, Product)
    assert created_product.name == product_name
    assert created_product.quantity == product_q
    assert created_product.price == product_p

    mock_uow.products.add.assert_called_once()
    added_product_arg = mock_uow.products.add.call_args[0][0]
    assert added_product_arg is created_product

    mock_uow.commit.assert_called_once()

def test_get_product_details_product_found(mock_uow, mocker):

    expected_product_id = 123
    expected_product = Product(
        id=expected_product_id, name="Testable Widget", quantity=10, price=25.00
    )

    mock_uow.products.get.return_value = expected_product

    service = WarehouseService(uow=mock_uow)

    retrieved_product = service.get_product_details(product_id=expected_product_id)

    mock_uow.products.get.assert_called_once_with(expected_product_id)
    assert retrieved_product is expected_product
    mock_uow.__enter__.assert_called_once()
    mock_uow.__exit__.assert_called_once()

def test_create_order_success_one_item(mocker, mock_uow): 
    service = WarehouseService(uow=mock_uow)

    test_product_id = 1
    test_quantity_to_order = 2
    products_to_order_details = [(test_product_id, test_quantity_to_order)]

    initial_stock_quantity = 5
    product_price = 10.0
    product_on_stock = Product(
        id=test_product_id, 
        name="Test Product", 
        quantity=initial_stock_quantity, 
        price=product_price
    )

    mock_uow.products.get.return_value = product_on_stock

    created_order = service.create_order(products_to_order_details)


    mock_uow.products.get.assert_called_once_with(test_product_id)
    assert isinstance(created_order, Order)
    assert len(created_order.items) == 1
    order_item = created_order.items[0]
    assert isinstance(order_item, OrderItem)
    assert order_item.product is product_on_stock
    assert order_item.quantity_ordered == test_quantity_to_order
    assert order_item.price_at_purchase == product_price

    expected_stock_after_order = initial_stock_quantity - test_quantity_to_order
    assert product_on_stock.quantity == expected_stock_after_order
    mock_uow.products.update.assert_called_once_with(product_on_stock)
    mock_uow.orders.add.assert_called_once_with(created_order)
    mock_uow.commit.assert_called_once()

    mock_uow.__enter__.assert_called_once()
    mock_uow.__exit__.assert_called_once_with(None, None, None) 


