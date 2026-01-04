import requests
import json
import base64
from datetime import datetime, timedelta
from django.conf import settings
import os

class MpesaIntegration:
    """
    MPESA Integration for Urban Foods Cafe
    Supports both Till Numbers (Buy Goods) and Paybill Numbers
    """

    def __init__(self):
        # MPESA API credentials from environment variables
        self.consumer_key = 'n1gp98HCA8gmOwt3vn4dhKG80Gwjdf1MXfoKbnESEiPmarUp'
        self.consumer_secret = 'C1W7E7P24lGGFZgokkGQ9qPudbGWxzLuCLphkK7wF72kctwoAIAPJL7Qmzc9SGuQ'
        self.shortcode = '174379'  # Default sandbox shortcode
        self.passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        self.paybill_number = '6960814' # Paybill number for liquor store
        self.account_number = 'URBANFOODS'  # Account number for paybill

        # API endpoints
        self.base_url = 'https://sandbox.safaricom.co.ke' if not os.environ.get('MPESA_PRODUCTION', False) else 'https://api.safaricom.co.ke'
        self.access_token_url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
        self.stk_push_url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'
        self.stk_query_url = f'{self.base_url}/mpesa/stkpushquery/v1/query'

        self.access_token = None
        self.token_expires_at = None

    def get_access_token(self):
        """Get MPESA API access token"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token

        try:
            response = requests.get(
                self.access_token_url,
                auth=(self.consumer_key, self.consumer_secret)
            )

            print("====== MPESA STK PUSH ======")
            print("STATUS:", response.status_code)
            print("RESPONSE:", response.text)
            
            print("============================")
            response.raise_for_status()

            data = response.json()
            self.access_token = data['access_token']

            # Token expires in 3599 seconds (1 hour)
            self.token_expires_at = datetime.now() + timedelta(seconds=3599)

            return self.access_token
        except Exception as e:
            print(f"Error getting access token: {e}")
            return None

    def generate_password(self, timestamp):
        """Generate password for STK push"""
        password_str = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode()
        return password

    def initiate_stk_push(self, phone_number, amount, account_reference, transaction_desc, store_type='food'):
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {'success': False, 'message': 'Failed to get access token'}

            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = self.generate_password(timestamp)

            is_production = os.environ.get('MPESA_PRODUCTION', 'false').lower() == 'true'

            if not is_production:
                # SANDBOX: PayBill ONLY
                transaction_type = "CustomerPayBillOnline"
                party_b = self.shortcode
                account_reference = account_reference
            else:
                # PRODUCTION (you can refine later)
                transaction_type = "CustomerPayBillOnline"
                party_b = self.shortcode

            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": transaction_type,
                "Amount": max(1, int(amount)),
                "PartyA": phone_number,
                "PartyB": party_b,
                "PhoneNumber": phone_number,
                "CallBackURL": os.environ.get(
                    'MPESA_CALLBACK_URL',
                    'https://urbandreamcafe.up.railway.app/mpesa/callback/'
                ),
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            response = requests.post(self.stk_push_url, json=payload, headers=headers)

            print("====== MPESA STK PUSH ======")
            print("STATUS:", response.status_code)
            print("RESPONSE:", response.text)
            print("PAYLOAD:", payload)
            print("============================")
            response.raise_for_status()

            result = response.json()

            if result.get('ResponseCode') == '0':
                return {
                    'success': True,
                    'checkout_request_id': result.get('CheckoutRequestID'),
                    'customer_message': result.get('CustomerMessage')
                }

            return {
                'success': False,
                'message': result.get('ResponseDescription', 'STK Push failed')
            }

        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': f'Network error: {e.response.text if e.response else str(e)}'}

    def query_stk_status(self, checkout_request_id):
        """Query STK push payment status"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {'success': False, 'message': 'Failed to get access token'}

            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = self.generate_password(timestamp)

            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            response = requests.post(self.stk_query_url, json=payload, headers=headers)

            print("====== MPESA STK PUSH ======")
            print("STATUS:", response.status_code)
            print("RESPONSE:", response.text)
            print("PAYLOAD:", payload)
            print("============================")
            response.raise_for_status()

            result = response.json()

            return {
                'success': True,
                'response_code': result.get('ResponseCode'),
                'response_description': result.get('ResponseDescription'),
                'result_code': result.get('ResultCode'),
                'result_desc': result.get('ResultDesc'),
                'callback_metadata': result.get('CallbackMetadata')
            }

        except Exception as e:
            return {'success': False, 'message': f'Error querying status: {str(e)}'}

    def format_phone_number(self, phone_number):
        """Format phone number to MPESA format (254XXXXXXXXX)"""
        phone = str(phone_number).strip()

        # Remove any spaces, hyphens, or brackets
        phone = ''.join(c for c in phone if c.isdigit())

        # Handle different formats
        if phone.startswith('0') and len(phone) == 10:
            # Format: 07XXXXXXXX or 01XXXXXXXX -> 2547XXXXXXXX or 2541XXXXXXXX
            phone = '254' + phone[1:]
        elif phone.startswith('+254') and len(phone) == 13:
            # Format: +2547XXXXXXXX -> 2547XXXXXXXX
            phone = phone[1:]
        elif phone.startswith('254') and len(phone) == 12:
            # Already in correct format
            pass
        elif len(phone) == 9 and phone.startswith('7'):
            # Format: 7XXXXXXXX -> 2547XXXXXXXX (missing leading 0)
            phone = '254' + phone
        elif len(phone) == 9 and phone.startswith('1'):
            # Format: 1XXXXXXXX -> 2541XXXXXXXX (missing leading 0)
            phone = '254' + phone
        else:
            raise ValueError('Invalid phone number format. Must be 10 digits starting with 0, 9 digits starting with 7 or 1, 12 digits starting with 254, or 13 digits starting with +254')

        return phone

# Global instance
mpesa = MpesaIntegration()
