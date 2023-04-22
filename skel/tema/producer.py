"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
from time import sleep


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time
        Thread.__init__(self, **kwargs)

    def provide(self, producer_id):
        """
        Auxiliary function used for providing products to the marketplace

        @type producer_id: Int
        @param producer_id: the producer's index/id
        """
        for product in self.products:
            # Parse name, quantity & timeout
            product_name = product[0]
            product_quantity = product[1]
            # time = product[2]

            if product_quantity == 0:
                return False

            count = 0
            while count != product_quantity:
                # Send product to the marketplace's stock
                result = self.marketplace.publish(producer_id, product_name)
                sleep(int(product[2]))
                if not result:
                    sleep(self.republish_wait_time)
                # else:
                #     sleep(time)
                count += 1

        return True

    def run(self):
        # Register new producer
        producer_id = self.marketplace.register_producer()

        while self.provide(producer_id):
            continue
