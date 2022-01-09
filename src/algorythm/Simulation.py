import math
from copy import deepcopy
from typing import Dict

from algorythm.SimulationWeights import SimulationWeights
from objects import Drone, Order
from algorythm import SimulationParameters
from utilities import Utilities
import logging


class Simulation:
    def __init__(self,
                 parameters: SimulationParameters,
                 weights: Dict[str, int] = None):
        self.parameters = deepcopy(parameters)
        if weights is not None:
            self.weights = weights
        else:
            self.weights = SimulationWeights.initialize_weights()
        self.score = 0

    def run(self):
        for turn in range(self.parameters.max_turns):
            if turn % 100 == 0:
                logging.info(f"Turn {turn}")
            for drone in self.parameters.drones:
                if drone.is_ready():
                    if drone.status == "NO_ORDER" and len(self.parameters.orders) > 0:
                        self.evaluate_orders()
                        drone.set_order(self.parameters.orders.pop(0))

                    if drone.status == "NO_TARGET":
                        if not drone.has_all_items():
                            self.evaluate_warehouses(drone, drone.order)
                            drone.reserve_goods(self.parameters.warehouses[0])
                            drone.fly_to_warehouse()
                        else:
                            drone.fly_to_order()

                    if drone.status == "READY_TO_LOAD":
                        drone.load()

                    if drone.status == "READY_TO_DELIVER":
                        drone.deliver()

                    if drone.status == "READY_TO_SCORE":
                        self.score += drone.calc_score(self.parameters.max_turns, turn)
                drone.update_time()
        logging.info(f"Total simulation score = {self.score}")

    def evaluate_orders(self):
        for order in self.parameters.orders:
            order.score = self.weights["wzl"] * order.amount + \
                          self.weights["wzr"] * len(order._items.keys())
            # TODO: Add more parameters
        self.parameters.orders.sort(reverse=True, key=lambda o: o.score)

    def evaluate_warehouses(self, drone: Drone, order: Order):
        for warehouse in self.parameters.warehouses:
            items_to_pick = 0
            for item_type in order._items.keys():
                if item_type in warehouse.items.keys():
                    items_to_pick += min(order._items[item_type].get_remains(), warehouse.items[item_type].current)

            if items_to_pick != 0:
                warehouse.score = self.weights["wmz"] * Utilities.calc_distance(order.coordinates, warehouse.coordinates) + \
                                  self.weights["wmd"] * Utilities.calc_distance(drone.coordinates, warehouse.coordinates) + \
                                  self.weights["wml"] * items_to_pick
            else:
                # There is nothing important in it
                warehouse.score = -math.inf

        self.parameters.warehouses.sort(reverse=True, key=lambda w: w.score)

    # def draw_map(self):
    #     for row in range(self.parameters.rows):
    #         for column in range(self.parameters.columns):
    #             no_object = True
    #             for warehouse in self.parameters.warehouses:
    #                 if [row, column] == warehouse.coordinates:
    #                     logging.info("W", end="")
    #                     no_object = False
    #             for order in self.parameters.orders:
    #                 if [row, column] == order.coordinates:
    #                     logging.info("O", end="")
    #                     no_object = False
    #             if no_object:
    #                 logging.info("-", end="")
    #         logging.info()
    #     logging.info()
