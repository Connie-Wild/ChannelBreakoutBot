# -*- coding: utf-8 -*-

import json
import requests
import time
import hmac
import hashlib
import urllib
from .exception import AuthException


class API(object):

    def __init__(self, api_key=None, api_secret=None, timeout=None):
        self.api_url = "https://api.bitflyer.com"
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout

    def request(self, endpoint, method="GET", params=None, private=True):
        url = self.api_url + endpoint
        body = ""
        auth_header = None

        if method == "POST":
            body = json.dumps(params)
        else:
            if params:
                body = "?" + urllib.parse.urlencode(params)

        if self.api_key and self.api_secret and private:
            access_timestamp = str(time.time())
            api_secret = str.encode(self.api_secret)
            text = str.encode(access_timestamp + method + endpoint + body)
            access_sign = hmac.new(api_secret,
                                   text,
                                   hashlib.sha256).hexdigest()
            auth_header = {
                "ACCESS-KEY": self.api_key,
                "ACCESS-TIMESTAMP": access_timestamp,
                "ACCESS-SIGN": access_sign,
                "Content-Type": "application/json"
            }

        try:
            with requests.Session() as s:
                if auth_header:
                    s.headers.update(auth_header)

                if method == "GET":
                    response = s.get(url, params=params, timeout=self.timeout)
                else:  # method == "POST":
                    response = s.post(url, data=json.dumps(params), timeout=self.timeout)
        except requests.RequestException as e:
            print(e)
            raise e

        content = ""
        if len(response.content) > 0:
            content = json.loads(response.content.decode("utf-8"))

        return content

    """HTTP Public API"""

    def board(self, **params):
        """Order Book

        API Type
        --------
        HTTP Public API

        Parameters
        ----------
        product_code: Designate "BTC_JPY", "FX_BTC_JPY" or "ETH_BTC".

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#order-book
        """
        endpoint = "/v1/board"
        return self.request(endpoint, params=params, private=False)

    def ticker(self, **params):
        """Ticker

        API Type
        --------
        HTTP Public API

        Parameters
        ----------
        product_code: Designate "BTC_JPY", "FX_BTC_JPY" or "ETH_BTC".

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#ticker
        """
        endpoint = "/v1/ticker"
        return self.request(endpoint, params=params, private=False)

    def executions(self, **params):
        """Execution History

        API Type
        --------
        HTTP Public API

        Parameters
        ----------
        product_code: Designate "BTC_JPY", "FX_BTC_JPY" or "ETH_BTC".
        count, before, after: See Pagination.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#execution-history
        """
        endpoint = "/v1/executions"
        return self.request(endpoint, params=params, private=False)

    def getboardstate(self, **params):
        """Order book status

        API Type
        --------
        HTTP Public API

        Parameters
        ----------
        product_code: Designate "BTC_JPY", "FX_BTC_JPY" or "ETC_BTC".

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=ja#%E6%9D%BF%E3%81%AE%E7%8A%B6%E6%85%8B
        """
        endpoint = "/v1/getboardstate"
        return self.request(endpoint, params=params, private=False)

    def gethealth(self, **params):
        """Exchange status
        This will allow you to determine the current status of the exchange.

        API Type
        --------
        HTTP Public API

        Parameters
        ----------
        product_code: Designate "BTC_JPY", "FX_BTC_JPY" or "ETH_BTC".
        count, before, after: See Pagination.

        Response
        --------
        status: one of the following levels will be displayed
            NORMAL: The exchange is operating.
            BUSY: The exchange is experiencing heavy traffic.
            VERY BUSY: The exchange is experiencing extremely heavy traffic. There is a possibility that orders will fail or be processed after a delay.
            STOP: The exchange has been stopped. Orders will not be accepted.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#exchange-status
        """
        endpoint = "/v1/gethealth"
        return self.request(endpoint, params=params, private=False)

    def getchats(self, **params):
        """ Chat
        Get an instrument list

        API Type
        --------
        HTTP Public API

        Parameters
        ----------
        from_date: This accesses a list of any new messages after this date.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#chat
        """
        endpoint = "/v1/getchats"
        return self.request(endpoint, params=params, private=False)

    """HTTP Private API"""

    def getbalance(self, **params):
        """Get Account Asset Balance

        API Type
        --------
        HTTP Private API

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#get-account-asset-balance
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/getbalance"
        return self.request(endpoint, params=params)

    def getcollateral(self, **params):
        """Get Margin Status

        API Type
        --------
        HTTP Private API

        Response
        --------
        collateral: This is the amount of deposited in Japanese Yen.
        open_position_pnl: This is the profit or loss from valuation.
        require_collateral: This is the current required margin.
        keep_rate: This is the current maintenance margin.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#get-margin-status
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/getcollateral"
        return self.request(endpoint, params=params)

    def getcollateralhistory(self, **params):
        """Get Margin Change History

        API Type
        --------
        HTTP Private API

        Response
        --------
        collateral: This is the amount of deposited in Japanese Yen.
        open_position_pnl: This is the profit or loss from valuation.
        require_collateral: This is the current required margin.
        keep_rate: This is the current maintenance margin.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#get-margin-change-history
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/getcollateralhistory"
        return self.request(endpoint, params=params)

    def getaddresses(self, **params):
        """Get Bitcoin/Ethereum Deposit Addresses

        API Type
        --------
        HTTP Private API

        Response
        --------
        type: "NORMAL" for general deposit addresses.
        currency_code: "BTC" for Bitcoin addresses and "ETH" for Ethereum addresses.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#get-bitcoin-ethereum-deposit-addresses
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/getaddresses"
        return self.request(endpoint, params=params)

    def getcoinins(self, **params):
        """Get Bitcoin/Ether Deposit History

        API Type
        --------
        HTTP Private API

        Parameters
        ----------
        count, before, after: See Pagination.

        Response
        --------
        status: If the Bitcoin deposit is being processed, it will be listed as "PENDING". If the deposit has been completed, it will be listed as "COMPLETED".

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#get-bitcoin-ether-deposit-history
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/getcoinins"
        return self.request(endpoint, params=params)

    def sendcoin(self, **params):
        """Bitcoin/Ethereum External Delivery

        API Type
        --------
        HTTP Private API

        Parameters
        ----------
        currency_code: Required. Type of currency to be sent. Please use "BTC" for Bitcoin and "ETH" for Ethereum.
        amount: Amount to be sent, specified as a number.
            If the currency_code is "BTC", then the units are in BTC.
            If the currency_code is `"ETC", then the units are in Ether.
        amount_text: Specifies the amount to be sent as a string. You are required to choose either amount or amount_text.
        address: Required. Specifies the address to which it will be sent.
            When currency_code is specified as "ETH", funds cannot be sent to a contract address.
            The address designated here will automatically be labeled as an external address.
        additional_fee: You may specify an additional fee to be paid to Bitcoin miners to prioritize their transaction. Standard fees based on transaction data size are paid by bitFlyer; however, the customer is responsible for any additional fees.
            Omitted values will be entered as "0".
            The upper limit is 0.0005 BTC .
            This can not be used if currency_code is specified as "ETH".

        Response
        --------
        message_id: Transaction Message Receipt ID

        If an error with a negative status value is returned, the transaction has not been broadcast.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#bitcoin-ethereum-external-delivery
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/sendcoin"
        return self.request(endpoint, "POST", params=params)

    def getcoinouts(self, **params):
        """Get Bitcoin/Ether Transaction History

        API Type
        --------
        HTTP Private API

        Parameters
        ----------
        count, before, after: See Pagination.
        message_id: You can confirm delivery status by checking a transaction receipt ID with the Bitcoin/Ethereum External Delivery API.

        Response
        --------
        status: If the remittance is being processed, it will be listed as "PENDING". If the remittance has been completed, it will be listed as "COMPLETED".

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#get-bitcoin-ether-transaction-history
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/getcoinouts"
        return self.request(endpoint, params=params)

    def getbankaccounts(self, **params):
        """Get Summary of Bank Accounts
        Returns a summary of bank accounts registered to your account.

        API Type
        --------
        HTTP Private API

        Response
        --------
        id: ID for the account designated for withdrawals.
        is_verified: Will be return true if the account is verified and capable of sending money.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#get-summary-of-bank-accounts
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/getbankaccounts"
        return self.request(endpoint, params=params)

    def getdeposits(self, **params):
        """Get Cash Deposits

        API Type
        --------
        HTTP Private API

        Parameters
        ----------
        count, before, after: See Pagination.

        Response
        --------
        status: If the cash deposit is being processed, it will be listed as "PENDING". If the deposit has been completed, it will be listed as "COMPLETED".

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#get-cash-deposits
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/getdeposits"
        return self.request(endpoint, params=params)

    def withdraw(self, **params):
        """Cancelling deposits

        API Type
        --------
        HTTP Private API

        Parameters
        ----------
        currency_code: Required. Currently only compatible with "JPY".
        bank_account_id: Required. Specify id of the bank account.
        amount: Required. This is the amount that you are canceling.

        Additional fees apply for withdrawals. Please see the Fees and Taxes page for reference.

        Response
        --------
        message_id: Transaction Message Receipt ID

        If an error with a negative status value is returned, the cancellation has not been committed.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#cancelling-deposits
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/withdraw"
        return self.request(endpoint, "POST", params=params)

    def getwithdrawals(self, **params):
        """Get Deposit Cancellation History

        API Type
        --------
        HTTP Private API

        Parameters
        ----------
        count, before, after: See Pagination.

        Response
        --------
        status: If the cancellation is being processed, it will be listed as "PENDING". If the cancellation has been completed, it will be listed as "COMPLETED".

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#get-deposit-cancellation-history
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/getwithdrawals"
        return self.request(endpoint, params=params)

    def sendchildorder(self, **params):
        """Send a New Order

        API Type
        --------
        HTTP Private API

        Parameters
        ----------
        product_code: Required. The product being ordered. Designate "BTC_JPY", "FX_BTC_JPY" or "ETH_BTC".
        child_order_type: Required. For limit orders, it will be "LIMIT". For market orders, "MARKET".
        side: Required. For buy orders, "BUY". For sell orders, "SELL".
        price: Specify the price. This is a required value if child_order_type has been set to "LIMIT".
        size: Required. Specify the order quantity.
        minute_to_expire: Specify the time in minutes until the expiration time. If omitted, the value will be 525600 (365 days).
        time_in_force: Specify any of the following execution conditions - "GTC", "IOC", or "FOK". If omitted, the value defaults to "GTC".

        Response
        --------
        If the parameters are correct, the status code will show 200 OK.

        child_order_acceptance_id: This is the ID for the API. To specify the order to return, please use this instead of child_order_id. Please confirm the item is either Cancel Order or Obtain Execution List.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#send-a-new-order
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/sendchildorder"
        return self.request(endpoint, "POST", params=params)

    def cancelchildorder(self, **params):
        """Cancel Order

        API Type
        --------
        HTTP Private API

        Parameters
        ----------
        product_code: Required. The product for the corresponding order. Designate "BTC_JPY", "FX_BTC_JPY" or "ETH_BTC".
        Please specify only one between child_order_id and child_order_acceptance_id

        child_order_id: ID for the canceling order.
        child_order_acceptance_id: Expects an ID from Send a New Order. When specified, the corresponding order will be cancelled.

        Response
        --------
        If the parameters are correct, the status code will show 200 OK.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#cancel-order
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/cancelchildorder"
        return self.request(endpoint, "POST", params=params)

    def sendparentorder(self, **params):
        """Submit New Parent Order (Special order)
        It is possible to place orders including logic other than simple limit orders (LIMIT) and market orders (MARKET). Such orders are handled as parent orders. By using a special order, it is possible to place orders in response to market conditions or place multiple associated orders.

        Please read about the types of special orders and their methods in the bitFlyer Lightning documentation on special orders.

        API Type
        --------
        HTTP Private API

        Parameters
        ----------
        order_method: The order method. Please set it to one of the following values. If omitted, the value defaults to "SIMPLE".
            "SIMPLE": A special order whereby one order is placed.
            "IFD": Conducts an IFD order. In this method, you place two orders at once, and when the first order is completed, the second order is automatically placed.
            "OCO": Conducts an OCO order. In this method, you place two orders at one, and when one of the orders is completed, the other order is automatically canceled.
            "IFDOCO": Conducts an IFD-OCO order. In this method, once the first order is completed, an OCO order is automatically placed.
        minute_to_expire: Specifies the time until the order expires in minutes. If omitted, the value defaults to 525600 (365 days).
        time_in_force: Specify any of the following execution conditions - "GTC", "IOC", or "FOK". If omitted, the value defaults to "GTC".
        parameters: Required value. This is an array that specifies the parameters of the order to be placed. The required length of the array varies depending upon the specified order_method.
            If "SIMPLE" has been specified, specify one parameter.
            If "IFD" has been specified, specify two parameters. The first parameter is the parameter for the first order placed. The second parameter is the parameter for the order to be placed after the first order is completed.
            If "OCO" has been specified, specify two parameters. Two orders are placed simultaneously based on these parameters.
            If "IFDOCO" has been specified, specify three parameters. The first parameter is the parameter for the first order placed. After the order is complete, an OCO order is placed with the second and third parameters.

        In the parameters, specify an array of objects with the following keys and values.

        product_code: Required value. This is the product to be ordered. Currently, only "BTC_JPY" is supported.
        condition_type: Required value. This is the execution condition for the order. Please set it to one of the following values.
            "LIMIT": Limit order.
            "MARKET": Market order.
            "STOP": Stop order.
            "STOP_LIMIT": Stop-limit order.
            "TRAIL": Trailing stop order.
        side: Required value. For buying orders, specify "BUY", for selling orders, specify "SELL".
        size: Required value. Specify the order quantity.
        price: Specify the price. This is a required value if condition_type has been set to "LIMIT" or "STOP_LIMIT".
        trigger_price: Specify the trigger price for a stop order. This is a required value if condition_type has been set to "STOP" or "STOP_LIMIT".
        offset: Specify the trail width of a trailing stop order as a positive integer. This is a required value if condition_type has been set to "TRAIL".

        Response
        --------
        If the parameters are correct, the status code will show 200 OK.

        parent_order_acceptance_id: This is the ID for the API. To specify the order to return, please use this instead of parent_order_id.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#submit-new-parent-order-special-order
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/sendparentorder"
        return self.request(endpoint, "POST", params=params)

    def cancelparentorder(self, **params):
        """Cancel parent order
        Parent orders can be canceled in the same manner as regular orders. If a parent order is canceled, the placed orders associated with that order will all be canceled.

        API Type
        --------
        HTTP Private API

        Parameters
        ----------
        product_code: Required. The product for the corresponding order. Designate "BTC_JPY", "FX_BTC_JPY" or "ETH_BTC".
        Please specify only one between parent_order_id and parent_order_acceptance_id

        parent_order_id: ID for the canceling order.
        parent_order_acceptance_id: Expects an ID from Submit New Parent Order. When specified, the corresponding order will be cancelled.

        Response
        --------
        If the parameters are correct, the status code will show 200 OK.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#cancel-parent-order
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/cancelparentorder"
        return self.request(endpoint, "POST", params=params)

    def cancelallchildorders(self, **params):
        """Cancel All Orders

        API Type
        --------
        HTTP Private API

        Parameters
        ----------
        product_code: The product for the corresponding order. Designate "BTC_JPY", "FX_BTC_JPY" or "ETH_BTC".

        Response
        --------
        If the parameters are correct, the status code will show 200 OK.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#cancel-all-orders
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/cancelallchildorders"
        return self.request(endpoint, "POST", params=params)

    def getchildorders(self, **params):
        """List Orders

        API Type
        --------
        HTTP Private API

        Parameters
        ----------
        product_code: Designate "BTC_JPY", "FX_BTC_JPY" or "ETH_BTC".
        count, before, after: See Pagination.
        child_order_state: When specified, return only orders that match the specified value. You must specify one of the following:
            ACTIVE: Return open orders
            COMPLETED: Return fully completed orders
            CANCELED: Return orders that have been cancelled by the customer
            EXPIRED: Return order that have been cancelled due to expiry
            REJECTED: Return failed orders
        parent_order_id: If specified, a list of all orders associated with the parent order is obtained.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#list-orders
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/getchildorders"
        return self.request(endpoint, params=params)

    def getparentorders(self, **params):
        """List Parent Orders

        API Type
        --------
        HTTP Private API

        Parameters
        ----------
        product_code: Designate "BTC_JPY", "FX_BTC_JPY" or "ETH_BTC".
        count, before, after: See Pagination.
        child_order_state: When specified, return only orders that match the specified value. You must specify one of the following:
            ACTIVE: Return open orders
            COMPLETED: Return fully completed orders
            CANCELED: Return orders that have been cancelled by the customer
            EXPIRED: Return order that have been cancelled due to expiry
            REJECTED: Return failed orders

        Response
        --------
        price and size values for parent orders with multiple associated orders are both reference values only.

        To obtain the detailed parameters for individual orders, use the API to obtain the details of the parent order. To obtain a list of associated orders, use the API to obtain the order list.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#list-parent-orders
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/getparentorders"
        return self.request(endpoint, params=params)

    def getparentorder(self, **params):
        """Get Parent Order Details

        API Type
        --------
        HTTP Private API

        Parameters
        ----------
        product_code: Designate "BTC_JPY", "FX_BTC_JPY" or "ETH_BTC".

        Please specify only parent_order_id or parent_order_acceptance_id.

        parent_order_id: The ID of the parent order in question.
        parent_order_acceptance_id: The acceptance ID for the API to place a new parent order. If specified, it returns the details of the parent order in question.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#get-parent-order-details
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/getparentorder"
        return self.request(endpoint, params=params)

    def getexecutions(self, **params):
        """List Executions

        API Type
        --------
        HTTP Private API

        Parameters
        ----------
        product_code: Designate "BTC_JPY", "FX_BTC_JPY" or "ETH_BTC".
        count, before, after: See Pagination.
        child_order_id: Optional. When specified, a list of stipulations related to the order will be displayed.
        child_order_acceptance_id: Optional. Expects an ID from Send a New Order. When specified, a list of stipulations related to the corresponding order will be displayed.

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#list-executions
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/getexecutions"
        return self.request(endpoint, params=params)

    def getpositions(self, **params):
        """

        API Type
        --------
        HTTP Private API

        Parameters
        ----------
        product_code: Currently supports only "FX_BTC_JPY".

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#get-open-interest-summary
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/getpositions"
        return self.request(endpoint, params=params)

    def gettradingcommission(self, **params):
        """

        API Type
        --------
        HTTP Private API

        Parameters
        ----------
        product_code: Required. Designate "BTC_JPY", "FX_BTC_JPY" or "ETH_BTC".

        Docs
        ----
        https://lightning.bitflyer.jp/docs?lang=en#get-trading-commission
        """
        if not all([self.api_key, self.api_secret]):
            raise AuthException()

        endpoint = "/v1/me/gettradingcommission"
        return self.request(endpoint, params=params)
