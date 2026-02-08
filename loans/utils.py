from datetime import date

def calculate_current_debt(loans):
    current_loans = loans.filter(end_date__gte=date.today())

    current_debt = 0
    for l in current_loans:
        remaining = l.loan_amount - (l.emis_paid_on_time * l.monthly_repayment)
        current_debt += max(0, remaining)
    
    return current_debt, current_loans


def calculate_credit_score(loans, customer):
        score = 0

        total_loans = loans.count()
        # in case tenure<emis_paid_on_time, (for some excel values this is true.)
        total_emis_paid = sum(min(l.emis_paid_on_time, l.tenure) for l in loans)
        total_possible_emis = sum(l.tenure for l in loans)


        # 1. EMI weightage = 40
        on_time_ratio = (total_emis_paid / total_possible_emis) if total_possible_emis else 0
        score += on_time_ratio * 40

        # 2. past loans = 20
        score += min(20, total_loans * 2)

        # 3. Loan activity this year = 20
        current_year_loans = loans.filter(start_date__year=date.today().year).count()
        score += min(20, current_year_loans * 5)

        # 4. Loan approved volume  = 20
        total_volume = sum(l.loan_amount for l in loans)
        volume_ratio = (total_volume / customer.approved_limit) if customer.approved_limit else 0
        score += min(20, volume_ratio * 20)

        credit_score = int(min(100, score))
        return credit_score




def calculate_emi(P, annual_rate, tenure_months):
    r = annual_rate / (12 * 100)

    if r == 0: # redundant, but if r == 0 then division error would be avoided.
        return P / tenure_months

    emi = (P * r * (1+r)**tenure_months) / ((1+r)**tenure_months - 1)
    return round(emi, 2)



def evaluate_eligibility(customer, data, loans):
    credit_score = calculate_credit_score(loans, customer)

    current_debt, current_loans = calculate_current_debt(loans)
    if current_debt > customer.approved_limit:
        print("not eligible for loan due to current debt being more than approved limit")
        credit_score = 0

    total_current_emi = sum(l.monthly_repayment for l in current_loans)
    approved = True

    if total_current_emi > 0.5 * customer.monthly_salary:
        print("not eligible for loan due to current emi being more than half of your monthly salary")
        approved = False

    corrected_rate = data["interest_rate"]

    if approved and 50 >= credit_score > 30 and corrected_rate < 12:
        corrected_rate = 12
    elif approved and 30 >= credit_score > 10 and corrected_rate < 16:
        corrected_rate = 16
    elif credit_score <= 10:
        print("not eligible for loan due to low credit score, ( your credit score<=10)")
        approved = False

    emi = calculate_emi(data["loan_amount"], corrected_rate, data["tenure"])
    new_total_emi = total_current_emi + emi

    # checking again for valid loan
    if data["loan_amount"] > customer.approved_limit:
        print("not eligible for loan due to amount being more than approved limit")
        approved = False

    if new_total_emi > 0.5 * customer.monthly_salary:
        print("not eligible for loan due to new emi being more than half of your monthly salary")
        approved = False

    return approved, corrected_rate, emi
