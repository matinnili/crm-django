from django.db import models

class calls(models):
    call_id = models.AutoField(primary_key=True)
    call_type = models.CharField(max_length=50)
    call_date = models.DateTimeField(auto_now_add=True)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.call_type} - {self.customer_name} ({self.call_date})"
# Create your models here.
