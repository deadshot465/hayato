import arrow
import json
import os
import requests
from datetime import datetime


class AuthenticationManager:
    token: str = ''
    expiry: datetime = arrow.utcnow().datetime

    @classmethod
    def login(cls):
        if arrow.utcnow().datetime < cls.expiry:
            return
        data = {
            'UserName': os.getenv('LOGIN_NAME'),
            'Password': os.getenv('LOGIN_PASS')
        }
        try:
            response = requests.post('https://tetsukizone.com/api/login', json=json.dumps(data))
            response.raise_for_status()
            res_data = json.loads(response.text)
            cls.token = str(res_data['token'])
            cls.expiry = arrow.get(str(res_data['expiry'])).datetime
        except requests.exceptions.HTTPError as ex:
            print('An error occurred when getting the login token: {}'.format(ex.response))
