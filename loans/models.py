from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

# Create your models here.

phone_validator = RegexValidator(
    regex=r'^\d{10}$',
    message="phone number is to be exactly 10 digits."
)
class Customer(models.Model):
    first_name = models.CharField(max_length=80)
    last_name =  models.CharField(max_length=80)
    age = models.IntegerField(validators=[MinValueValidator(0)])
    phone_number = models.CharField(max_length=10, validators = [phone_validator])
    monthly_salary = models.IntegerField(validators=[MinValueValidator(0)])
    approved_limit = models.IntegerField(validators=[MinValueValidator(0)])
    current_debt = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="loans")
    loan_amount = models.FloatField(validators=[MinValueValidator(0)])
    tenure = models.IntegerField(validators=[MinValueValidator(0)])
    interest_rate = models.FloatField(validators=[MinValueValidator(0)])
    monthly_repayment = models.FloatField(validators = [MinValueValidator(0)])
    emis_paid_on_time = models.IntegerField(validators= [MinValueValidator(0)])
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Loan {self.id} -> Customer {self.customer.id}"