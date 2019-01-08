from pybitflyer_v2 import pybitflyer_v2
import json
import logging
import time
import datetime

#注文処理をまとめている
class BFOrder:
    def __init__(self):
        # config.jsonの読み込み
        f = open('config/config.json', 'r', encoding="utf-8")
        config = json.load(f)
        self.product_code = config["product_code"]
        self.key = config["key"]
        self.secret = config["secret"]
        self.api = pybitflyer_v2.API(api_key=self.key, api_secret=self.secret, timeout=5)

    def limit(self, side, price, size, minute_to_expire=None):
        logging.info("Order: Limit. Side : {}".format(side))
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.sendchildorder(product_code=self.product_code, child_order_type="LIMIT", side=side,
                                               price=price, size=size, minute_to_expire=minute_to_expire)
        except:
            pass
        logging.debug(response)
        while ("status" in response or not response or (response and not "JRF" in str(response))):
            logging.error(response)
            time.sleep(0.1)
            try:
                response = self.api.sendchildorder(product_code=self.product_code, child_order_type="LIMIT", side=side,
                                                   price=price, size=size, minute_to_expire=minute_to_expire)
            except:
                pass
        return response

    def market(self, side, size, minute_to_expire=None):
        logging.info("Order: Market. Side : {}".format(side))
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.sendchildorder(product_code=self.product_code, child_order_type="MARKET", side=side,
                                               size=size, minute_to_expire=minute_to_expire)
        except:
            pass
        logging.debug(response)
        while ("status" in response or not response or (response and not "JRF" in str(response))):
            logging.error(response)
            time.sleep(0.1)
            try:
                response = self.api.sendchildorder(product_code=self.product_code, child_order_type="MARKET", side=side,
                                                   size=size, minute_to_expire=minute_to_expire)
            except:
                pass
        return response

    def stop(self, side, size, trigger_price, minute_to_expire=None):
        logging.info("Order: Stop. Side : {}".format(side))
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.sendparentorder(order_method="SIMPLE", parameters=[
                {"product_code": self.product_code, "condition_type": "STOP", "side": side, "size": size,
                 "trigger_price": trigger_price, "minute_to_expire": minute_to_expire}])
        except:
            pass
        logging.debug(response)
        while ("status" in response or not response or (response and not "JRF" in str(response))):
            logging.error(response)
            time.sleep(0.1)
            try:
                response = self.api.sendparentorder(order_method="SIMPLE", parameters=[
                    {"product_code": self.product_code, "condition_type": "STOP", "side": side, "size": size,
                     "trigger_price": trigger_price, "minute_to_expire": minute_to_expire}])
            except:
                pass
        return response

    def stop_limit(self, side, size, trigger_price, price, minute_to_expire=None):
        logging.info("Order: Stop limit. Side : {}".format(side))
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.sendparentorder(order_method="SIMPLE", parameters=[
                {"product_code": self.product_code, "condition_type": "STOP_LIMIT", "side": side, "size": size,
                 "trigger_price": trigger_price, "price": price, "minute_to_expire": minute_to_expire}])
        except:
            pass
        logging.debug(response)
        while ("status" in response or not response or (response and not "JRF" in str(response))):
            logging.error(response)
            time.sleep(0.1)
            try:
                response = self.api.sendparentorder(order_method="SIMPLE", parameters=[
                    {"product_code": self.product_code, "condition_type": "STOP_LIMIT", "side": side, "size": size,
                     "trigger_price": trigger_price, "price": price, "minute_to_expire": minute_to_expire}])
            except:
                pass
        return response

    def trailing(self, side, size, offset, minute_to_expire=None):
        logging.info("Order: Trailing. Side : {}".format(side))
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.sendparentorder(order_method="SIMPLE", parameters=[
                {"product_code": self.product_code, "condition_type": "TRAIL", "side": side, "size": size,
                 "offset": offset, "minute_to_expire": minute_to_expire}])
        except:
            pass
        logging.debug(response)
        while ("status" in response or not response or (response and not "JRF" in str(response))):
            logging.error(response)
            time.sleep(0.1)
            try:
                response = self.api.sendparentorder(order_method="SIMPLE", parameters=[
                    {"product_code": self.product_code, "condition_type": "TRAIL", "side": side, "size": size,
                     "offset": offset, "minute_to_expire": minute_to_expire}])
            except:
                pass
        return response

    def ticker(self):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.ticker(product_code=self.product_code)
        except:
            pass
        logging.debug(response)
        while ("status" in response or not response or (response and not "timestamp" in str(response))):
            logging.error(response)
            time.sleep(0.1)
            try:
                response = self.api.ticker(product_code=self.product_code)
            except:
                pass
        return response

    def getexecutions(self, order_id):
        start = time.time()
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.getexecutions(product_code=self.product_code, child_order_acceptance_id=order_id)
        except:
            pass
        logging.debug(response)
        while ("status" in response or not response or (response and not "JRF" in str(response))):
            if not response:
                logging.debug(response)
            else:
                logging.error(response)
            time.sleep(0.25)
            try:
                response = self.api.getexecutions(product_code=self.product_code, child_order_acceptance_id=order_id)
            except:
                pass
        logging.info("Finished:%ss", round(time.time() - start, 3))
        return response

    def getboardstate(self):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.getboardstate(product_code=self.product_code)
        except:
            pass
        logging.debug(response)
        while ("status" in response or not response or (response and not "health" in str(response))):
            logging.error(response)
            time.sleep(0.1)
            try:
                response = self.api.getboardstate(product_code=self.product_code)
            except:
                pass
        return response

    def getcollateral(self):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.getcollateral()
        except:
            pass
        logging.debug(response)
        while ("status" in response or not response or (response and not "collateral" in str(response))):
            logging.error(response)
            time.sleep(0.1)
            try:
                response = self.api.getcollateral()
            except:
                pass
        return response

    def getpositions(self):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.getpositions(product_code=self.product_code)
        except:
            pass
        logging.debug(response)
        while "status" in response or (response and not "side" in str(response)):
            logging.error(response)
            time.sleep(0.1)
            try:
                response = self.api.getpositions(product_code=self.product_code)
            except:
                pass
        return response

    def cancelallchildorders(self):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.cancelallchildorders(product_code=self.product_code)
        except:
            pass
        logging.debug(response)
        while response:
            logging.error(response)
            time.sleep(0.1)
            try:
                response = self.api.cancelallchildorders(product_code=self.product_code)
            except:
                pass
        return response

    def getboard(self):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.board(product_code=self.product_code)
        except:
            pass
        logging.debug(response)
        while ("status" in response or not response or (response and not "mid_price" in str(response))):
            logging.error(response)
            time.sleep(0.1)
            try:
                response = self.api.board(product_code=self.product_code)
            except:
                pass
        return response

    def getchildorders(self, child_order_state='ACTIVE'):
        response = {"status": "internalError in bforder.py"}
        try:
            response = self.api.getchildorders(product_code=self.product_code, child_order_state=child_order_state)
        except:
            pass
        logging.debug(response)
        while "status" in response or (response and not "side" in str(response)):
            logging.error(response)
            time.sleep(0.1)
            try:
                response = self.api.getchildorders(product_code=self.product_code, child_order_state=child_order_state)
            except:
                pass
        return response
