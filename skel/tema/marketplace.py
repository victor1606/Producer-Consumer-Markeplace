"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import unittest
from logging.handlers import RotatingFileHandler
from threading import Lock
import logging
from time import gmtime


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        # Locks used for thread synchro

        self.producer_lock = Lock()
        self.customer_lock = Lock()

        self.queue_size_per_producer = queue_size_per_producer

        # Two-dimensional arrays containing producers/carts & their products
        self.producer_list = []
        self.customer_carts = []

        # Logging mechanism configuration
        logging.basicConfig(handlers=[RotatingFileHandler(
            'marketplace.log', maxBytes=100000, backupCount=10)],
                            level=logging.INFO,
                            format='[%(asctime)s] %(levelname)s %(message)s',
                            datefmt='%Y-%m-%dT %H:%M:%S')
        logging.Formatter.converter = gmtime
        self.logger = logging.getLogger()

        self.logger.info("Marketplace constructor: queue_size_per_producer - %s",
                         queue_size_per_producer)

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        self.logger.info("register_producer - returns id %d", len(self.producer_list))

        # Add new producer to the list
        with self.producer_lock:
            self.producer_list.append([])

        # The producer's id will be the list's length - 1
        return len(self.producer_list)

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        returns True or False. If the caller receives False, it should wait and then try again.
        """
        self.logger.info("publish - producer %d adds product %s", producer_id, product)

        # Adjust index
        producer_id -= 1

        # Ensure mutex between threads
        with self.producer_lock:
            if self.queue_size_per_producer > len(self.producer_list[producer_id]):
                self.producer_list[producer_id].append(product)
                return True

        # self.logger.info("publish - producer %d cannot add %s", producer_id, product)
        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        returns an int representing the cart_id
        """
        self.logger.info("new_cart - returns id of new cart %d", len(self.customer_carts))

        # Ensure mutex between threads
        with self.customer_lock:
            # Add new empty product list for new producer
            self.customer_carts.append([])

        return len(self.customer_carts)

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        returns True or False. If the caller receives False, it should wait and then try again
        """
        self.logger.info("add_to_cart - adds %s to cart %d",
                         product, cart_id)

        # Adjust index
        cart_id -= 1

        # Ensure mutex between threads
        with self.customer_lock:
            # Search for the product in all the product lists
            for producer_product_list in self.producer_list:
                # If found, add the product to cart and remove it from stock
                if product in producer_product_list:
                    self.customer_carts[cart_id].append(product)
                    producer_product_list.remove(product)

                    return True

        # self.logger.info("Product %s not found", product)
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        self.logger.info("remove_from_cart - product %s is removed from cart %d",
                         product, cart_id)

        # Adjust index
        cart_id -= 1

        # Ensure mutex between threads
        with self.customer_lock:
            # Remove product from cart
            self.customer_carts[cart_id].remove(product)

            # Check if the removed product can be added back to the producer's list
            idx = 0
            while idx < len(self.producer_list):
                if self.queue_size_per_producer > len(self.producer_list[idx]):
                    # Add the product back to the producer's list
                    self.producer_list[idx].append(product)
                    return True
                idx += 1

        return False

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        self.logger.info("place_order - cart %d was ordered", cart_id)

        # Adjust index
        cart_id -= 1
        return self.customer_carts[cart_id]


class TestMarketplace(unittest.TestCase):
    """
    Class for testing all the functionalities of the marketplace class
    """

    def setUp(self):
        """
        Initialize marketplace
        """
        self.marketplace = Marketplace(5)

    def test_register_product(self):
        """
        Method to check register_product from Marketplace
        """
        rang = range(200)
        for i in rang:
            self.assertEqual(
                self.marketplace.register_producer(), i, "Not the expected id")

    def test_publish(self):
        """
        Method to check publish from Marketplace
        """
        producer_id = self.marketplace.register_producer()
        prod1 = {
            "product_type": "Coffee",
            "name": "Indonezia",
            "acidity": 5.05,
            "roast_level": "MEDIUM",
            "price": 1
        }.__str__()

        prod2 = {
            "product_type": "Tea",
            "name": "Wild Cherry",
            "type": "Black",
            "price": 5
        }.__str__()
        expected_list = [prod1, prod2]
        self.marketplace.publish(producer_id, prod1)
        self.marketplace.publish(producer_id, prod2)

        self.assertEqual(
            self.marketplace.producers_products[producer_id], expected_list,
            "Not the expected products")

    def test_new_cart(self):
        """
        Method to check new_cart from Marketplace
        """
        rang = range(200)
        for i in rang:
            self.assertEqual(
                self.marketplace.new_cart(), i, "Not the expected id")

    def test_add_to_cart(self):
        """
        Method to check add_to_cart from Marketplace
        """
        cart_id = self.marketplace.new_cart()
        producer_id = self.marketplace.register_producer()
        prod1 = {
            "product_type": "Coffee",
            "name": "Indonezia",
            "acidity": 5.05,
            "roast_level": "MEDIUM",
            "price": 1
        }.__str__()

        prod2 = {
            "product_type": "Tea",
            "name": "Wild Cherry",
            "type": "Black",
            "price": 5
        }.__str__()

        self.marketplace.publish(producer_id, prod1)
        self.marketplace.publish(producer_id, prod2)

        self.marketplace.add_to_cart(cart_id=cart_id, product=prod1)

        # check for adding to cart
        self.assertEqual(self.marketplace.consumers_carts[cart_id], [
                         prod1], "Not the expected cart content")

        # check for removing from producer
        self.assertEqual(self.marketplace.producers_products[producer_id], [
                         prod2], "Not the expected cart content")

    def test_remove_from_cart(self):
        """
        Method to check remove_from_cart from Marketplace
        """
        cart_id = self.marketplace.new_cart()
        producer_id = self.marketplace.register_producer()
        prod1 = {
            "product_type": "Coffee",
            "name": "Indonezia",
            "acidity": 5.05,
            "roast_level": "MEDIUM",
            "price": 1
        }.__str__()

        prod2 = {
            "product_type": "Tea",
            "name": "Wild Cherry",
            "type": "Black",
            "price": 5
        }.__str__()

        self.marketplace.publish(producer_id, prod1)
        self.marketplace.publish(producer_id, prod2)

        self.marketplace.add_to_cart(cart_id=cart_id, product=prod1)

        self.marketplace.remove_from_cart(cart_id=cart_id, product=prod1)

        self.assertEqual(self.marketplace.consumers_carts[cart_id], [
        ], "Not the expected cart content")

        # check for removing from producer
        self.assertEqual(self.marketplace.producers_products[producer_id], [prod2,
                         prod1], "Not the expected cart content")

    def test_place_order(self):
        """
        Method to check place_order from Marketplace
        """
        cart_id = self.marketplace.new_cart()
        producer_id = self.marketplace.register_producer()
        prod1 = {
            "product_type": "Coffee",
            "name": "Indonezia",
            "acidity": 5.05,
            "roast_level": "MEDIUM",
            "price": 1
        }.__str__()

        prod2 = {
            "product_type": "Tea",
            "name": "Wild Cherry",
            "type": "Black",
            "price": 5
        }.__str__()

        self.marketplace.publish(producer_id, prod1)
        self.marketplace.publish(producer_id, prod2)

        self.marketplace.add_to_cart(cart_id=cart_id, product=prod1)
        cart = self.marketplace.consumers_carts[cart_id]
        order = self.marketplace.place_order(cart_id=cart_id)

        self.assertEqual(cart, order, "Not the expected order")