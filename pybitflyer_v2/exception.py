# -*- coding: utf-8 -*-


class AuthException(Exception):

    def __init__(self):
        msg = "Please specify your valid API Key and API Secret."
        super(AuthException, self).__init__(msg)
