from rest_framework import serializers
from .models import Customer, Loan

class RegisterCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
            "age",
            "phone_number",
            "monthly_salary",
            "approved_limit",
        ]
        read_only_fields = ["id", "approved_limit"]

    def create(self, validated_data):
        salary = validated_data["monthly_salary"]

        # approved_limit = 36 * monthly_salary (rounded to nearest lakh)
        approved_limit = round((36 * salary) / 100000) * 100000

        validated_data["approved_limit"] = approved_limit

        # creates the user, doesn't save it here. user is saved in the api.
        return super().create(validated_data)
    


class CheckEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()


class CustomerMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "first_name", "last_name", "phone_number", "age"]


class LoanDetailSerializer(serializers.ModelSerializer):
    customer = CustomerMiniSerializer()

    class Meta:
        model = Loan
        fields = [
            "id",
            "customer",
            "loan_amount",
            "interest_rate",
            "monthly_repayment",
            "tenure"
        ]


class CustomerLoansSerializer(serializers.ModelSerializer):
    repayments_left = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = [
            "id",
            "loan_amount",
            "interest_rate",
            "monthly_repayment",
            "repayments_left"
        ]

    def get_repayments_left(self, obj):
        return max(0, obj.tenure - obj.emis_paid_on_time)
