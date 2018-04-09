import pybitflyer
import json
import logging

#注文処理をまとめている
class BFOrder:
    def __init__(self):
        #config.jsonの読み込み
        f = open('config.json', 'r')
        config = json.load(f)
        self.product_code = config["product_code"]
        self.key = config["key"]
        self.secret = config["secret"]
        self.api = pybitflyer.API(self.key, self.secret)

    def limit(self, side, price, size, minute_to_expire=None):
        logging.info("Order: Limit. Side : {}".format(side))
        response = {"status":"internalError in order.py"}
        try:
            response = self.api.sendchildorder(product_code=self.product_code, child_order_type="LIMIT", side=side, price=price, size=size, minute_to_expire = minute_to_expire)
        except:
            pass
        logging.debug(response)
        while "status" in response:
            try:
                response = self.api.sendchildorder(product_code=self.product_code, child_order_type="LIMIT", side=side, price=price, size=size, minute_to_expire = minute_to_expire)
            except:
                pass
            logging.debug(response)
            time.sleep(3)
        return response

    def market(self, side, size, minute_to_expire= None):
        logging.info("Order: Market. Side : {}".format(side))
        response = {"status": "internalError in order.py"}
        try:
            response = self.api.sendchildorder(product_code=self.product_code, child_order_type="MARKET", side=side, size=size, minute_to_expire = minute_to_expire)
        except:
            pass
        logging.debug(response)
        while "status" in response:
            try:
                response = self.api.sendchildorder(product_code=self.product_code, child_order_type="MARKET", side=side, size=size, minute_to_expire = minute_to_expire)
            except:
                pass
            logging.debug(response)
            time.sleep(3)
        return response

    def ticker(self):
        response = {"status": "internalError in order.py"}
        try:
            response = self.api.ticker(product_code=self.product_code)
        except:
            pass
        logging.debug(response)
        while "status" in response:
            try:
                response = self.api.ticker(product_code=self.product_code)
            except:
                pass
            logging.debug(response)
        return response

    def getexecutions(self, order_id):
        response = {"status": "internalError in order.py"}
        try:
            response = self.api.getexecutions(product_code=self.product_code, child_order_acceptance_id=order_id)
        except:
            pass
        logging.debug(response)
        while ("status" in response or not response):
            try:
                response = self.api.getexecutions(product_code=self.product_code, child_order_acceptance_id=order_id)
            except:
                pass
            logging.debug(response)
            time.sleep(0.5)
        return response

    def getboardstate(self):
        response = {"status": "internalError in order.py"}
        try:
            response = self.api.getboardstate(product_code=self.product_code)
        except:
            pass
        logging.debug(response)
        while "status" in response:
            try:
                response = self.api.getboardstate(product_code=self.product_code)
            except:
                pass
            logging.debug(response)
            time.sleep(0.5)
        return response

    def stop(self, side, size, trigger_price, minute_to_expire=None):
        logging.info("Order: Stop. Side : {}".format(side))
        response = {"status": "internalError in order.py"}
        try:
            response = self.api.sendparentorder(order_method="SIMPLE", parameters=[{"product_code": self.product_code, "condition_type": "STOP", "side": side, "size": size,"trigger_price": trigger_price, "minute_to_expire": minute_to_expire}])
        except:
            pass
        logging.debug(response)
        while "status" in response:
            try:
                response = self.api.sendparentorder(order_method="SIMPLE", parameters=[{"product_code": self.product_code, "condition_type": "STOP", "side": side, "size": size,"trigger_price": trigger_price, "minute_to_expire": minute_to_expire}])
            except:
                pass
            logging.debug(response)
            time.sleep(3)
        return response

    def stop_limit(self, side, size, trigger_price, price, minute_to_expire=None):
        logging.info("Side : {}".format(side))
        response = {"status": "internalError in order.py"}
        try:
            response = self.api.sendparentorder(order_method="SIMPLE", parameters=[{"product_code": self.product_code, "condition_type": "STOP_LIMIT", "side": side, "size": size,"trigger_price": trigger_price, "price": price, "minute_to_expire": minute_to_expire}])
        except:
            pass
        logging.debug(response)
        while "status" in response:
            try:
                response = self.api.sendparentorder(order_method="SIMPLE", parameters=[{"product_code": self.product_code, "condition_type": "STOP_LIMIT", "side": side, "size": size,"trigger_price": trigger_price, "price": price, "minute_to_expire": minute_to_expire}])
            except:
                pass
            logging.debug(response)
        return response

    def trailing(self, side, size, offset, minute_to_expire=None):
        logging.info("Side : {}".format(side))
        response = {"status": "internalError in order.py"}
        try:
            response = self.api.sendparentorder(order_method="SIMPLE", parameters=[{"product_code": self.product_code, "condition_type": "TRAIL", "side": side, "size": size, "offset": offset, "minute_to_expire": minute_to_expire}])
        except:
            pass
        logging.debug(response)
        while "status" in response:
            try:
                response = self.api.sendparentorder(order_method="SIMPLE", parameters=[{"product_code": self.product_code, "condition_type": "TRAIL", "side": side, "size": size, "offset": offset, "minute_to_expire": minute_to_expire}])
            except:
                pass
            logging.debug(response)
        return response
