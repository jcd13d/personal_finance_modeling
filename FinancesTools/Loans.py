import pandas as pd
import numpy as np

import FinancesTools.FinancesObjects
from FinancesTools.FinancesObjects import FinanceObject, ColumnObject, ZeroColumn, SpecifiedColumn
from FinancesTools.Income import IncomeColumn


class MonthlyCostCol(IncomeColumn):
    # should hit cash col like income col already does
    def __init__(self, name, start_timestamp, end_timestamp, cost_amount):
        super(MonthlyCostCol, self).__init__(name, start_timestamp, end_timestamp, -1*cost_amount)


class OneTimePayment(IncomeColumn):
    # hits cash (default)
    def __init__(self, name, timestamp, amount):
        super(OneTimePayment, self).__init__(name, timestamp, timestamp, amount)


class OneTimeLiability(OneTimePayment):
    def __init__(self, name, timestamp, amount):
        super(OneTimePayment, self).__init__(name, timestamp, timestamp, -1*amount)

    def get_net_cash_delta(self):
        # doesnt hit cash
        return ZeroColumn(self.name, self.start_timestamp, self.end_timestamp).get_column_df()

    def get_liabilities_delta(self):
        # hits liabilities
        return self.column_df


class LoanInterestPaid(SpecifiedColumn):
    def __init__(self, name, start_timestamp, end_timestamp, column_values):
        super(LoanInterestPaid, self).__init__(name, start_timestamp, end_timestamp, column_values)

    def get_net_cash_delta(self):
        # Doesnt impact net columns, just shows the interest portion of loan payment
        return ZeroColumn(self.name, self.start_timestamp, self.end_timestamp).get_column_df()

class LoanPrinciplePaid(SpecifiedColumn):
    def __init__(self, name, start_timestamp, end_timestamp, column_values):
        super(LoanPrinciplePaid, self).__init__(name, start_timestamp, end_timestamp, column_values)

    def get_net_cash_delta(self):
        # Doesnt impact net cash, this portion applied to liabilities
        return ZeroColumn(self.name, self.start_timestamp, self.end_timestamp).get_column_df()

    def get_liabilities_delta(self):
        # hits liabilities - principal portion of loan payment pays down what you owe
        return self.get_column_df()


class Loan(FinanceObject):
    def __init__(self, name, start_timestamp, end_timestamp, loan_amount, rate):
        super(Loan, self).__init__()
        self.zero_day = start_timestamp
        self.start = FinancesTools.FinancesObjects.Utility.add_months_to_timestamp(start_timestamp, 1)
        self.end = FinancesTools.FinancesObjects.Utility.add_months_to_timestamp(end_timestamp, 1)
        self.rate = rate
        self.amount = loan_amount
        self.add_column_object(MonthlyCostCol(f"{name} service", self.start, self.end, self.get_loan_payment()))
        self.add_column_object(OneTimePayment(f"{name} cash", self.zero_day, loan_amount))
        self.add_column_object(OneTimeLiability(f"{name} liability", self.zero_day, loan_amount))
        interest, principal = self.get_interest_and_principal()
        # print(interest)
        # print(principal)
        # raise("test")
        self.add_column_object(LoanInterestPaid(f"{name} interest", self.start, self.end, interest))
        self.add_column_object(LoanPrinciplePaid(f"{name} principal", self.start, self.end, principal))

    def get_loan_payment(self):
        df = ColumnObject.build_index(self.start, self.end)
        discount_factors = 1 / ((1 + self.rate / 12) ** (df.index.to_numpy() + 1))
        payment_per_month = self.amount / discount_factors.sum()
        return payment_per_month

    def get_interest_and_principal(self):
        pmt = self.get_loan_payment()
        payments = [pmt for i in range(len(ColumnObject.build_index(self.start, self.end)))]
        loan_balance = self.amount
        interest_paid = []
        principal_paid = []
        for payment in payments:
            interest_paid.append(loan_balance*self.rate/12)
            principal_paid.append(payment - interest_paid[-1])
            loan_balance = loan_balance - principal_paid[-1]

        return np.array(interest_paid), np.array(principal_paid)











