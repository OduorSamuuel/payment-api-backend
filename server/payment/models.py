from django.db import models

class PesapalTransaction(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    ipn_id = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.amount} {self.currency}"
