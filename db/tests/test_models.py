from uuid import uuid4

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from db.models import (
    Category,
    Product,
    Comment,
    Order,
    ShippingInfo,
    Cart,
    CartItem,
)


class UserModelTest(TestCase):
    """
    Tests custom user model
    """

    def test_create_user_with_email_successful(self):
        """
        Tests if it is possible to create a user with email address
        """
        email = "test@mitest.com"
        pwd = "testpassword"

        user = get_user_model().objects.create_user(email=email, password=pwd)

        self.assertEqual(email, user.email)
        self.assertTrue(user.check_password(pwd))

    def test_new_user_email_normalized(self):
        """
        Tests if email for new user is normalized
        """
        email = "test@MiTest.cOm"

        user = get_user_model().objects.create_user(email=email)

        self.assertEqual(user.email, email.lower())

    def test_create_superuser_with_email_successful(self):
        """
        Tests if it is possible to create a superuser with email address
        """
        email = "test@mitest.com"
        pwd = "testpassword"

        user = get_user_model().objects.create_superuser(email=email, password=pwd)
        self.assertEqual(email, user.email)
        self.assertTrue(user.check_password(pwd))

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_user_with_email_exception(self):
        """
        Tests if the create user raise an error when it has'nt email address
        """

        with self.assertRaises(ValueError):
            user = get_user_model().objects.create_user(email=None)

    def test_create_superuser_password_exception(self):
        """
        Tests if the create superuser raise an error when it has'nt password
        """
        email = "test@mitest.com"

        with self.assertRaises(ValueError):
            user = get_user_model().objects.create_superuser(email=email, password=None)

    def test_create_superuser_email_exception(self):
        """
        Tests if the create superuser raise an error when it has'nt password
        """

        pwd = "testpassword"

        with self.assertRaises(ValueError):
            user = get_user_model().objects.create_superuser(email=None, password=pwd)


class CategoryModelTest(TestCase):
    """
    Tests Category model
    """

    def test_create_category_successful(self):
        """
        Tests if can create a Category
        """
        category = Category.objects.create(title="TestCategory")

        self.assertEqual("TestCategory", category.title)

        self.assertEqual("TestCategory", str(category))

    def test_create_child_category_successful(self):
        """
        Tests if can create a Category
        """
        parent_category = Category.objects.create(title="TestParentCategory")

        child_category = Category.objects.create(
            title="TestChildCategory", parent=parent_category
        )

        self.assertEqual("TestChildCategory", child_category.title)
        self.assertEqual(child_category.parent, parent_category)

        self.assertEqual("TestChildCategory", str(child_category))

    def test_create_existing_category_reject(self):
        """
        Tests if can't create an existing category
        """
        Category.objects.create(title="TestCategory")

        with self.assertRaises(IntegrityError):
            Category.objects.create(title="TestCategory")


class ProductModelTest(TestCase):
    """
    Tests Product model
    """

    def setUp(self):
        self.category = Category.objects.create(title="TestCategory")

        self.mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl/1.com",
                "testimgurl/2.com",
                "testimgurl/3.com",
            ],
            "stock": 11,
            "category": self.category,
            "sold": 11,
        }

    def test_create_product_successful(self):
        """
        Tests if its possible create product
        """

        product = Product.objects.create(**self.mock_product)

        self.assertEqual(product.title, self.mock_product["title"])
        self.assertEqual(product.price, self.mock_product["price"])
        self.assertEqual(product.description, self.mock_product["description"])
        self.assertEqual(product.images[0], self.mock_product["images"][0])
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.rate, 5.0)

        self.assertEqual(self.mock_product["title"], str(product))

    def test_create_existing_product_reject(self):
        """
        Tests if can't create an existing product
        """

        Product.objects.create(**self.mock_product)

        with self.assertRaises(IntegrityError):
            Product.objects.create(**self.mock_product)

    def test_create_comment_product_method_successful(self):
        """
        Tests if product has create_comment and update his rate with it
        """
        product = Product.objects.create(**self.mock_product)

        user = get_user_model().objects.create_user(email="testemail@test.com")

        comment_payload = {
            "user": user,
            "subject": "Test Subject",
            "content": "Test Content",
            "rate": 3.2,
        }

        comment = product.create_comment(**comment_payload)

        self.assertEqual(product.rate, 3.2)
        self.assertEqual(comment.product, product)
        self.assertEqual(comment.user, user)

    def test_create_comment_product_method_sets_avg_rate_successful(self):
        """
        Tests if product has create_comment and update his rate with avg
        """
        product = Product.objects.create(**self.mock_product)

        user = get_user_model().objects.create_user(email="testemail@test.com")

        comment_payload = {
            "user": user,
            "subject": "Test Subject",
            "content": "Test Content",
            "rate": 2,
        }
        product.create_comment(**comment_payload)

        comment_payload["rate"] = 4
        product.create_comment(**comment_payload)

        self.assertEqual(product.rate, 3)

    def test_create_comment_product_method_negative_rate_reject(self):
        """
        Tests if product can't create comment with negative rate
        """
        product = Product.objects.create(**self.mock_product)

        user = get_user_model().objects.create_user(email="testemail@test.com")

        comment_payload = {
            "user": user,
            "subject": "Test Subject",
            "content": "Test Content",
            "rate": -0.1,
        }

        with self.assertRaises(ValueError):
            product.create_comment(**comment_payload)

    def test_create_comment_product_method_greater_rate_reject(self):
        """
        Tests if product can't create comment with rate greater than 5
        """
        product = Product.objects.create(**self.mock_product)

        user = get_user_model().objects.create_user(email="testemail@test.com")

        comment_payload = {
            "user": user,
            "subject": "Test Subject",
            "content": "Test Content",
            "rate": 5.1,
        }

        with self.assertRaises(ValueError):
            product.create_comment(**comment_payload)


class ShippingInfoModelTest(TestCase):
    """
    Tests Shipping info model
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testemail@test.com", first_name="Test", last_name="Testi"
        )

        self.mock_shipping_info = {
            "user": self.user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }

    def test_create_shipping_info_successful(self):
        """
        Tests if model can create shipping info
        """
        shipping_info = ShippingInfo.objects.create(**self.mock_shipping_info)

        self.assertEqual(shipping_info.user, self.user)
        self.assertEqual(shipping_info.address, self.mock_shipping_info["address"])

        self.assertEqual(
            f"Shipping Info of {self.user.get_full_name()}", str(shipping_info)
        )

    def test_create_shipping_info_no_name_user_successful(self):
        """
        Tests if model can create shipping info
        """
        new_user = get_user_model().objects.create_user(email="testi@testemail.com")

        new_mock_shipping_info = {**self.mock_shipping_info, "user": new_user}
        shipping_info = ShippingInfo.objects.create(**new_mock_shipping_info)

        self.assertEqual(f"Shipping Info of {new_user.email}", str(shipping_info))


class OrderModelTest(TestCase):
    """
    Tests order model
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testemail@test.com", first_name="Test", last_name="Testi"
        )

        self.category = Category.objects.create(title="TestCategory")
        self.mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl/1.com",
                "testimgurl/2.com",
                "testimgurl/3.com",
            ],
            "stock": 11,
            "category": self.category,
            "sold": 11,
        }
        self.product = Product.objects.create(**self.mock_product)

        self.mock_shipping_info = {
            "user": self.user,
            "address": "Test address",
            "receiver": "test receiver name",
            "receiver_dni": 12345678,
        }
        self.shipping_info = ShippingInfo.objects.create(**self.mock_shipping_info)

        self.mock_order = {
            "id": uuid4(),
            "buyer": self.user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": self.shipping_info,
        }

    def test_create_order_successful(self):
        """
        Tests if model can create an order
        """
        order = Order.objects.create(**self.mock_order)

        self.assertEqual(order.id, self.mock_order["id"])
        self.assertEqual(order.buyer, self.user)
        self.assertEqual(order.products, self.mock_order["products"])
        self.assertEqual(order.shipping_info, self.shipping_info)
        self.assertTrue(order.created_at)

        self.assertEqual(f"Order of {order.buyer.get_full_name()}", str(order))

    def test_create_order_no_name_user_successful(self):
        """
        Tests if model can create an order
        """
        new_user = get_user_model().objects.create_user(email="testi@testemail.com")

        new_mock_order = {**self.mock_order, "buyer": new_user}
        order = Order.objects.create(**new_mock_order)

        self.assertEqual(f"Order of {order.buyer.email}", str(order))

    def test_create_order_without_id_successful(self):
        """
        Tests if model can create an order without id
        """
        mock_order = {
            "buyer": self.user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": self.shipping_info,
        }

        order = Order.objects.create(**mock_order)

        self.assertTrue(order.id)
        self.assertEqual(order.buyer, self.user)
        self.assertEqual(order.products, self.mock_order["products"])
        self.assertEqual(order.shipping_info, self.shipping_info)
        self.assertTrue(order.created_at)

        self.assertEqual(f"Order of {order.buyer.get_full_name()}", str(order))

    def test_create_some_orders_without_id_successful(self):
        """
        Tests if model can create an order without id
        """
        mock_order = {
            "buyer": self.user,
            "products": [
                {"id": self.product.id, "title": self.product.title, "count": 4}
            ],
            "shipping_info": self.shipping_info,
        }

        first_order = Order.objects.create(**mock_order)
        second_order = Order.objects.create(**mock_order)
        thirst_order = Order.objects.create(**mock_order)

        self.assertNotEqual(first_order.id, second_order)
        self.assertNotEqual(thirst_order.id, second_order)

    def test_create_existing_order_reject(self):
        """
        Tests if can't create an existing order
        """

        Order.objects.create(**self.mock_order)

        with self.assertRaises(IntegrityError):
            Order.objects.create(**self.mock_order)


class CommentModelTest(TestCase):
    """
    Tests Comment model
    """

    def setUp(self):
        category = Category.objects.create(title="TestCategory")

        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl/1.com",
                "testimgurl/2.com",
                "testimgurl/3.com",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }

        self.product = Product.objects.create(**mock_product)  # create product

        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testPass"  # create user
        )

    def test_create_comment_successful(self):
        """
        Tests if can create a comment
        """

        mock_comment = {
            "user": self.user,
            "product": self.product,
            "subject": "Test comment subject",
            "content": "Test comment content",
            "rate": 4.3,
        }

        comment = Comment.objects.create(**mock_comment)

        self.assertEqual(self.user, comment.user)
        self.assertEqual(self.product, comment.product)
        self.assertEqual(mock_comment["subject"], comment.subject)

        self.assertEqual(mock_comment["subject"], str(comment))

        self.assertTrue(comment.created_at)


class CartModelTest(TestCase):
    """
    Tests Cart model
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testemail@test.com", first_name="Test", last_name="Testi"
        )

    def test_create_cart_successful(self):
        """
        Tests if can create a cart
        """
        mock_cart = {"user": self.user}
        cart = Cart.objects.create(**mock_cart)

        self.assertEqual(cart.user, self.user)
        self.assertEqual(cart.total_items, 0)
        self.assertTrue(cart.last_modification)

        self.assertEqual(str(cart), f"{str(self.user)}'s Cart")

    def test_create_cart_with_existent_user_reject(self):
        mock_cart = {"user": self.user}
        Cart.objects.create(**mock_cart)

        with self.assertRaises(IntegrityError):
            Cart.objects.create(**mock_cart)

    def test_get_products_in_cart_method_successful(self):
        """
        Test if cart has get_products method and return current products
        """
        # Cart creation
        mock_cart = {"user": self.user}
        cart = Cart.objects.create(**mock_cart)

        # Product creation
        category = Category.objects.create(title="TestCategory")
        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }
        product = Product.objects.create(**mock_product)

        # Cart item creation
        mock_cart_item = {"product": product, "count": 5}
        new_product = cart.add_product(**mock_cart_item)

        products = cart.get_products()

        self.assertTrue(products)
        self.assertEqual(products[0], new_product)

        self.assertEqual(cart.total_items, mock_cart_item["count"])

    def test_add_product_in_cart_method_successful(self):
        """
        Test if cart has add_product method and update total items
        """
        # Cart creation
        mock_cart = {"user": self.user}
        cart = Cart.objects.create(**mock_cart)

        # Product creation
        category = Category.objects.create(title="TestCategory")
        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }
        product = Product.objects.create(**mock_product)

        # Cart item creation
        mock_cart_item = {"product": product, "count": 5}
        new_product = cart.add_product(**mock_cart_item)

        self.assertTrue(new_product)

        self.assertEqual(new_product.product, product)
        self.assertEqual(new_product.count, mock_cart_item["count"])

        products = cart.get_products()
        self.assertEqual(products[0], new_product)

        self.assertEqual(cart.total_items, mock_cart_item["count"])

    def test_add_product_in_cart_method_without_params_reject(self):
        """
        Test if cart has add_product method with constraints in params
        """
        # Cart creation
        mock_cart = {"user": self.user}
        cart = Cart.objects.create(**mock_cart)

        with self.assertRaises(ValueError):
            cart.add_product()

    def test_add_product_in_cart_method_no_duplication_successful(self):
        """
        Test if cart has add_product method and update total items
        without duplication of product
        """
        # Cart creation
        mock_cart = {"user": self.user}
        cart = Cart.objects.create(**mock_cart)

        # Product creation
        category = Category.objects.create(title="TestCategory")
        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }
        product = Product.objects.create(**mock_product)

        # Cart item creation
        mock_cart_item = {"product": product, "count": 5}
        cart.add_product(**mock_cart_item)
        cart.add_product(**mock_cart_item)

        products = cart.get_products()
        self.assertEqual(len(products), 1)

        self.assertEqual(cart.total_items, mock_cart_item["count"] * 2)

    def test_remove_product_in_cart_method_successful(self):
        """
        Test if cart has remove_product method and update total items
        """
        # Cart creation
        mock_cart = {"user": self.user}
        cart = Cart.objects.create(**mock_cart)

        # Product creation
        category = Category.objects.create(title="TestCategory")
        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }
        product = Product.objects.create(**mock_product)

        # Cart item creation
        mock_cart_item = {"product": product, "count": 5}
        new_product = cart.add_product(**mock_cart_item)

        # Execution of delete method
        cart.remove_product(product)

        products = cart.get_products()
        self.assertFalse(products)

        self.assertEqual(cart.total_items, 0)

    def test_remove_product_in_cart_method_no_existing_item_reject(self):
        """
        Test if cart has remove_product method and reject when cart don't have product
        """
        # Cart creation
        mock_cart = {"user": self.user}
        cart = Cart.objects.create(**mock_cart)

        # Product creation
        category = Category.objects.create(title="TestCategory")
        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }
        product = Product.objects.create(**mock_product)

        # Execution of delete method
        with self.assertRaises(cart.DoesNotExist):
            cart.remove_product(product)

    def test_remove_product_in_cart_method_no_product_reject(self):
        """
        Test if cart has remove_product method and reject when no pass products
        """
        # Cart creation
        mock_cart = {"user": self.user}
        cart = Cart.objects.create(**mock_cart)

        # Execution of delete method
        with self.assertRaises(ValueError):
            cart.remove_product()

    def test_get_total_price_in_cart_method_with_single_product_successful(self):
        """
        Test if cart has get_total_price method and return price
        """
        # Cart creation
        mock_cart = {"user": self.user}
        cart = Cart.objects.create(**mock_cart)

        # Product creation
        category = Category.objects.create(title="TestCategory")
        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }
        product = Product.objects.create(**mock_product)

        # Cart item creation
        mock_cart_item = {"product": product, "count": 5}
        cart.add_product(**mock_cart_item)

        price = cart.get_total_price()

        self.assertTrue(price)
        self.assertEqual(price, product.price * mock_cart_item["count"])

    def test_get_total_price_in_cart_method_with_some_products_successful(self):
        """
        Test if cart has get_total_price method and return price
        """
        # Cart creation
        mock_cart = {"user": self.user}
        cart = Cart.objects.create(**mock_cart)

        # Product creation
        category = Category.objects.create(title="TestCategory")
        mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": category,
            "sold": 11,
        }
        first_product = Product.objects.create(**mock_product)

        mock_product["title"] = "Test Title 2"
        mock_product["price"] = 232
        second_product = Product.objects.create(**mock_product)

        # Cart item creation
        mock_cart_item = {"product": first_product, "count": 5}
        first_cart_item = cart.add_product(**mock_cart_item)

        mock_cart_item = {"product": second_product, "count": 2}
        second_cart_item = cart.add_product(**mock_cart_item)

        price = cart.get_total_price()

        self.assertTrue(price)
        self.assertEqual(
            price,
            first_product.price * first_cart_item.count
            + second_product.price * second_cart_item.count,
        )


class CartItemModelTest(TestCase):
    """
    Tests Cart item model
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testemail@test.com", first_name="Test", last_name="Testi"
        )

        self.mock_cart = {"user": self.user}
        self.cart = Cart.objects.create(**self.mock_cart)

        self.category = Category.objects.create(title="TestCategory")
        self.mock_product = {
            "title": "Test title",
            "description": "Test description",
            "price": 1111,
            "images": [
                "testimgurl.com/1",
                "testimgurl.com/2",
                "testimgurl.com/3",
            ],
            "stock": 11,
            "category": self.category,
            "sold": 11,
        }
        self.product = Product.objects.create(**self.mock_product)

    def test_create_cart_item_successful(self):
        """
        Tests if can create a cart item
        """
        mock_cart_item = {"cart": self.cart, "product": self.product, "count": 5}
        cart_item = CartItem.objects.create(**mock_cart_item)

        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.count, mock_cart_item["count"])

        self.assertEqual(
            str(cart_item),
            f"{cart_item.product.title} to {cart_item.cart.user.email}'s Cart",
        )
