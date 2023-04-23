"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread, Lock
from time import sleep


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time

        # Lock used for mutual exclusion while printing order
        self.print_lock = Lock()

        Thread.__init__(self, **kwargs)

    def run(self):
        # For each cart
        for cart in self.carts:
            # Add new empty cart
            cart_id = self.marketplace.new_cart()

            # For every command, parse the type, product and quantity
            for command in cart:
                command_type = command["type"]
                product_name = command["product"]
                product_quantity = command["quantity"]

                if command_type == "add":
                    # Add products to the cart
                    count = 0
                    while count != product_quantity:
                        result = self.marketplace.add_to_cart(cart_id, product_name)

                        # Retry adding after waiting the specified retry time
                        if not result:
                            sleep(self.retry_wait_time)
                        else:
                            count += 1

                elif command_type == "remove":
                    # Remove products from the cart
                    count = 0
                    while count != product_quantity:
                        self.marketplace.remove_from_cart(cart_id, product_name)
                        count += 1

            # Place order
            order = self.marketplace.place_order(cart_id)

            # Print order
            with self.print_lock:
                for product in order:
                    print("%s bought %s" % (self.name, str(product)))
