"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from threading import Lock


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

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
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
        # Adjust index
        producer_id -= 1

        # Ensure mutex between threads
        with self.producer_lock:
            if self.queue_size_per_producer > len(self.producer_list[producer_id]):
                self.producer_list[producer_id].append(product)
                return True
        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        returns an int representing the cart_id
        """
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

        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        # Adjust index
        cart_id -= 1

        # Ensure mutex between threads
        with self.customer_lock:
            # Remove product from cart
            self.customer_carts[cart_id].remove(product)

            # Check if the removed product can be added back to the producer's list
            for idx, producer in enumerate(self.producer_list):
                if self.queue_size_per_producer > len(self.producer_list[idx]):
                    # Add the product back to the producer's list
                    self.producer_list[idx].append(product)
                    return True

        return False

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        # Adjust index
        cart_id -= 1

        return self.customer_carts[cart_id]
