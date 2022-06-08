import numpy as np
import pandas as pd
from FinancesTools.FinancesObjects import FinanceObject, Utility, SpecifiedColumn, ColumnObject, ZeroColumn
from FinancesTools.Loans import OneTimePayment
from FinancesTools.Income import IncomeColumn


class OneTimeCost(OneTimePayment):
    # hits cash (default)
    def __init__(self, name, timestamp, amount):
        super(OneTimeCost, self).__init__(name, timestamp, -1*amount)


class OneTimeAsset(OneTimePayment):
    def __init__(self, name, timestamp, amount):
        super(OneTimeAsset, self).__init__(name, timestamp, amount)

    def get_assets_delta(self):
        return self.get_column_df()

    def get_net_cash_delta(self):
        return ZeroColumn(self.name, self.start_timestamp, self.end_timestamp).get_column_df()


class AppreciationSchedule(SpecifiedColumn):
    # base class for an appreciation schedule, can have compound interest, manual schedyle etc.
    def __init__(self, name, start_timestamp, end_timestamp, column):
        super(AppreciationSchedule, self).__init__(name, start_timestamp, end_timestamp, column)

    # hits assets col
    def get_assets_delta(self):
        return self.get_column_df()


class IncomeSchedule(SpecifiedColumn):
    def __init__(self, name, start_timestamp, end_timestamp, column):
        super(IncomeSchedule, self).__init__(name, start_timestamp, end_timestamp, column)

    # income hits cash
    def get_net_cash_delta(self):
        return self.get_column_df()


class CashFlowAsset(FinanceObject):
    def __init__(self, name, start_timestamp, end_timestamp, asset_cost, appreciation_type, appreciation_args, income_type, income_args):
        super(CashFlowAsset, self).__init__()
        self.name = name
        self.end_passed = end_timestamp
        self.zero_day = start_timestamp
        self.start = Utility.add_months_to_timestamp(start_timestamp, 1)
        self.end = Utility.add_months_to_timestamp(end_timestamp, 1)
        self.asset_cost = asset_cost
        self.appreciation = self.get_appreciation_schedule(appreciation_type, appreciation_args)
        self.income = self.get_income_schedule(income_type, income_args)

        # columns
        # asset purchase cost
        self.add_column_object(OneTimeCost(f"{name} Cost", self.zero_day, self.asset_cost))
        # asset worth
        self.add_column_object(OneTimeAsset(f"{name} Asset Delta", self.zero_day, self.asset_cost))
        # asset appreciation
        self.add_column_object(self.appreciation)
        # asset cash flow in
        self.add_column_object(self.income)

    def get_appreciation_schedule(self, appreciation_type, appreciation_args):
        if appreciation_type == "constant":
            return self.generate_constant_appreciation_schedule(**appreciation_args)
        elif appreciation_type == "specified":
            return self.generate_specified_appreciation_schedule(**appreciation_args)

    def get_income_schedule(self, income_type, income_args):
        if income_type == "constant":
            return self.generate_constant_income_schedule(**income_args)
        elif income_type == "proportional":
            return self.generate_proportional_income_schedule(**income_args)

    def generate_constant_appreciation_schedule(self, appreciation_amount):
        schedule = [appreciation_amount for i in range(len(ColumnObject.build_index(self.start, self.end)))]
        return AppreciationSchedule(f"{self.name} appreciation", self.start, self.end, schedule)

    def generate_specified_appreciation_schedule(self, csv_loc):
        schedule_df = pd.read_csv(csv_loc)
        assert min(schedule_df['timestamp']) == self.zero_day
        assert max(schedule_df['timestamp']) == self.end
        apprectiation_monthly = []
        for pct in schedule_df['pct'].shift(periods=1):
            monthly_pct = pct/12
            if not apprectiation_monthly:
                apprectiation_monthly.append(self.asset_cost)
            else:
                apprectiation_monthly.append(apprectiation_monthly[-1]*(1+monthly_pct))
        cu_appreciation = (pd.Series(apprectiation_monthly) - self.asset_cost).diff()
        return AppreciationSchedule(f"{self.name} appreciation", self.zero_day, self.end, cu_appreciation)

    def generate_constant_income_schedule(self, income_amount):
        schedule = [income_amount for i in range(len(ColumnObject.build_index(self.start, self.end)))]
        return IncomeSchedule(f"{self.name} income", self.start, self.end, schedule)

    def generate_proportional_income_schedule(self, proportion):
        asset_value = [self.asset_cost + x for x in self.appreciation.column.fillna(0).cumsum().fillna(0)]
        print(self.appreciation.column)
        print(asset_value)
        schedule = [i*proportion for i in asset_value]
        return IncomeSchedule(f"{self.name} income", self.zero_day, self.end, schedule)
