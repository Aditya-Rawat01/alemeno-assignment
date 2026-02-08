from django.core.management.base import BaseCommand
from django.db import transaction
import pandas as pd
from loans.models import Customer, Loan

class Command(BaseCommand):
    help = "Ingest initial Excel data"

    def handle(self, *args, **kwargs):
        customers_df = pd.read_excel("data/customer_data.xlsx")
        loans_df = pd.read_excel("data/loan_data.xlsx")

        with transaction.atomic():
            # Bulk create customers
            customers = [
                Customer(
                    id=row["Customer ID"],
                    first_name=row["First Name"],
                    last_name=row["Last Name"],
                    age=row["Age"],
                    phone_number=str(row["Phone Number"]),
                    monthly_salary=row["Monthly Salary"],
                    approved_limit=row["Approved Limit"],
                )
                for _, row in customers_df.iterrows()
            ]
            Customer.objects.bulk_create(customers, ignore_conflicts=True)
            # dict for easy lookup for loans
            customer_map = {c.id: c for c in Customer.objects.all()}

            # Bulk create loans
            loans = [
                Loan(
                    id=row["Loan ID"],
                    customer=customer_map[row["Customer ID"]],
                    loan_amount=row["Loan Amount"],
                    tenure=row["Tenure"],
                    interest_rate=row["Interest Rate"],
                    monthly_repayment=row["Monthly payment"],
                    emis_paid_on_time=row["EMIs paid on Time"],
                    start_date=row["Date of Approval"],
                    end_date=row["End Date"],
                )
                for _, row in loans_df.iterrows()
            ]
            Loan.objects.bulk_create(loans, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS("Data ingested successfully"))