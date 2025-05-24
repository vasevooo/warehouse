import pytest
from domain.models import Order, Product, OrderItem


@pytest.fixture
def sample_product() -> Product:
    return Product(id=1, name='Test Product', quantity=10, price=100)

@pytest.fixture
def product_a() -> Product:
    return Product(id=2, name="Product A", quantity=5, price=50.0)

@pytest.fixture
def product_b() -> Product:
    return Product(id=3, name="Product B", quantity=8, price=20.0)

order_cost_test_cases = [
    ("empty_order", [], 0.0),
    ("single_item_order", [("sample_product", 2)], 200.0), # sample_product.price = 100.0
    (
        "multiple_items_order",
        [("product_a", 1), ("product_b", 3)], # product_a.price = 50.0, product_b.price = 20.0
        110.0 # (1*50) + (3*20) = 50 + 60 = 110
    ),
]



def test_add_one_item_to_order(sample_product: Product):
    order = Order(id=1)

    quantity_to_order = 2
    order.add_item(product=sample_product, quantity_to_order=quantity_to_order)

    assert len(order.items) == 1
    added_item = order.items[0]
    assert isinstance(added_item, OrderItem)
    assert added_item.product == sample_product
    assert added_item.quantity_ordered == quantity_to_order
    assert added_item.price_at_purchase == sample_product.price

def test_add_item_with_negative_quantity_raises_value_error(sample_product: Product):
    order = Order(id=1)

    with pytest.raises(ValueError) as excinfo:
        order.add_item(product=sample_product, quantity_to_order=-2)
    assert str(excinfo.value) == 'Quantity to order must be positive'

@pytest.mark.parametrize("case_name, items_to_add, expected_total_cost", order_cost_test_cases)
def test_order_total_cost(
    case_name: str,
    items_to_add: list,
    expected_total_cost: float,
    sample_product: Product,
    product_a: Product, 
    product_b: Product
):
    order = Order(id=1)

    products_map = {
        "sample_product": sample_product,
        "product_a": product_a,
        "product_b": product_b
    }

    for product_name, quantity in items_to_add:
        product_to_add = products_map[product_name]
        order.add_item(product_to_add, quantity)

    assert order.total_order_cost == expected_total_cost



