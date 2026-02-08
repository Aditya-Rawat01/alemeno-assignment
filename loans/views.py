from dateutil.relativedelta import relativedelta
from loans.models import Customer, Loan
from loans.utils import calculate_current_debt, calculate_credit_score, calculate_emi, evaluate_eligibility
from django.shortcuts import render
from datetime import date

# Create your views here.

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterCustomerSerializer, CheckEligibilitySerializer, LoanDetailSerializer, CustomerLoansSerializer

# creates a new customer: /register_customer
@api_view(["POST"])
def register_customer(request):
    serializer = RegisterCustomerSerializer(data=request.data)

    if serializer.is_valid():
        # after creating and returning the user, it is saved from here.
        customer = serializer.save()
        return Response(RegisterCustomerSerializer(customer).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# checks eligibility for the loan approval:

@api_view(["POST"])
def check_eligibility(request):
    serializer = CheckEligibilitySerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    data = serializer.validated_data
    try:
        customer = Customer.objects.get(id=data["customer_id"])
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)
    loans = Loan.objects.filter(customer=customer)

    approved, corrected_rate, emi = evaluate_eligibility(customer, data, loans )

    return Response({
        "customer_id": customer.id,
        "approval": approved,
        "interest_rate": data["interest_rate"],
        "corrected_interest_rate": corrected_rate,
        "tenure": data["tenure"],
        "monthly_installment": emi
    })


@api_view(["POST"])
def create_loan(request):
    serializer = CheckEligibilitySerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    data = serializer.validated_data

    try:
        customer = Customer.objects.get(id=data["customer_id"])
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)

    loans = Loan.objects.filter(customer=customer)

    approved, corrected_rate, emi = evaluate_eligibility(customer, data, loans)

    if not approved:
        return Response({
            "loan_id": None,
            "customer_id": customer.id,
            "loan_approved": False,
            "message": "Loan not approved",
            "monthly_installment": emi
        }, status=status.HTTP_201_CREATED)

    # Create Loan
    loan = Loan.objects.create(
        customer=customer,
        loan_amount=data["loan_amount"],
        tenure=data["tenure"],
        interest_rate=corrected_rate,
        monthly_repayment=emi,
        emis_paid_on_time=0,
        start_date=date.today(),
        end_date = date.today() + relativedelta(months=data["tenure"])
    )

    return Response({
        "loan_id": loan.id,
        "customer_id": customer.id,
        "loan_approved": True,
        "message": "Loan approved",
        "monthly_installment": emi
    }, status = 201)


@api_view(["GET"])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.select_related("customer").get(id=loan_id)
    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=404)

    serializer = LoanDetailSerializer(loan)
    return Response(serializer.data)


@api_view(["GET"])
def view_loans(request, customer_id):
    if not Customer.objects.filter(id=customer_id).exists():
        return Response({"error": "Customer not found"}, status=404)

    loans = Loan.objects.filter(customer_id=customer_id)

    serializer = CustomerLoansSerializer(loans, many=True)
    return Response(serializer.data)
