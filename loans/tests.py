from datetime import date
from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from django.urls import reverse
from loans.models import Customer, Loan

class CreateLoanTest(APITestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            age=30,
            phone_number="9999999999",
            monthly_salary=50000,
            approved_limit=1800000
        )
        Loan.objects.create(
        customer=self.customer,
        loan_amount=50000,
        tenure=12,
        interest_rate=10,
        monthly_repayment=4500,
        emis_paid_on_time=12,
        start_date=date(2024,1,1),
        end_date=date(2025,1,1)
        )

    def test_create_loan_success(self):
        url = "/api/create-loan/"

        data = {
            "customer_id": self.customer.id,
            "loan_amount": 100000,
            "interest_rate": 10,
            "tenure": 12
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["loan_approved"])
        self.assertIsNotNone(response.data["loan_id"])
