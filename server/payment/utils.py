import requests
from django.conf import settings
import json

class PesapalAPI:
    def __init__(self):
        self.base_url = settings.PESAPAL_BASE_URL
        self.consumer_key = settings.PESAPAL_CONSUMER_KEY
        self.consumer_secret = settings.PESAPAL_CONSUMER_SECRET
        self.token = None

    def get_auth_token(self):
        url = f"{self.base_url}/Auth/RequestToken"
        payload = {
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            self.token = response.json().get('token')
            return self.token
        return None

    def register_ipn(self):
        if not self.token:
            self.get_auth_token()
        
        url = f"{self.base_url}/URLSetup/RegisterIPN"
        headers = {'Authorization': f'Bearer {self.token}'}
        payload = {
            "url": settings.PESAPAL_IPN_URL,
            "ipn_notification_type": "GET"
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    def submit_order(self, order_data):
        if not self.token:
            self.get_auth_token()
            
        url = f"{self.base_url}/Transactions/SubmitOrderRequest"
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(url, json=order_data, headers=headers)
        return response.json()
