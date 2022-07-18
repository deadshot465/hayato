import json
import logging
from datetime import datetime

import arrow
import requests
from services.configuration_service import configuration_service


class AuthenticationService:
    token: str = ''
    expiry: datetime = arrow.utcnow().datetime

    @classmethod
    def login(cls):
        if arrow.utcnow().datetime < cls.expiry:
            return
        data = {
            'user_name': configuration_service.login_name,
            'password': configuration_service.login_pass
        }
        try:
            response = requests.post(configuration_service.api_endpoint + '/login', json=data)
            response.raise_for_status()
            res_data = json.loads(response.text)
            cls.token = str(res_data['token'])
            cls.expiry = arrow.get(str(res_data['expiry'])).datetime
        except requests.exceptions.HTTPError as ex:
            logging.error('An error occurred when getting the login token: %s' % ex.response)
