from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .utils import PesapalAPI
from .models import PesapalTransaction
import uuid


class InitiatePaymentView(APIView):
    def post(self, request):
        pesapal = PesapalAPI()
       
        # First get auth token
        token = pesapal.get_auth_token()
        if not token:
            return Response({"error": "Failed to get authentication token"},
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Register IPN
        ipn_response = pesapal.register_ipn()
        if not ipn_response.get('ipn_id'):
            return Response({"error": "Failed to register IPN"},
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare order data
        order_data = {
            "id": str(uuid.uuid4()),
            "currency": request.data.get('currency', 'KES'),
            "amount": float(request.data.get('amount')),
            "description": request.data.get('description'),
            "callback_url": settings.PESAPAL_CALLBACK_URL,
            "notification_id": ipn_response['ipn_id'],
            "billing_address": request.data.get('billing_address')
        }
        
        # Submit order
        order_response = pesapal.submit_order(order_data)
        
        if order_response.get('order_tracking_id'):
            # Save transaction
            PesapalTransaction.objects.create(
                transaction_id=order_data['id'],
                amount=order_data['amount'],
                currency=order_data['currency'],
                status='PENDING',
                ipn_id=ipn_response['ipn_id']
            )
            
            return Response(order_response)
        
        return Response({"error": "Failed to create order"},
                      status=status.HTTP_400_BAD_REQUEST)

class PaymentCallbackView(APIView):
    def get(self, request):
        # Handle the callback from Pesapal
        order_tracking_id = request.GET.get('OrderTrackingId')
        order_merchant_reference = request.GET.get('OrderMerchantReference')
        order_notification_type = request.GET.get('OrderNotificationType')
        
        # Update transaction status
        try:
            transaction = PesapalTransaction.objects.get(
                transaction_id=order_merchant_reference)
            transaction.status = order_notification_type
            transaction.save()
            
            return Response({"status": "success"})
        except PesapalTransaction.DoesNotExist:
            return Response({"error": "Transaction not found"},
                          status=status.HTTP_404_NOT_FOUND)