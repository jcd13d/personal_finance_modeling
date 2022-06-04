import pandas as pd
from FinancesTools.FinancesObjects import FinanceObject, ColumnObject, ZeroColumn


class IncomeColumn(ColumnObject):
    def __init__(self, name, start_timestamp, end_timestamp, income_amount):
        super(IncomeColumn, self).__init__(name, start_timestamp, end_timestamp)
        self.income_amount = income_amount

    def get_column_df(self):
        if self.column_df is None:
            self.column_df = self.build_index(self.start_timestamp, self.end_timestamp)
            self.column_df[self.name] = self.income_amount
            return self.column_df
        else:
            return self.column_df

    def get_net_cash_delta(self):
        return self.column_df

    def get_assets_delta(self):
        return ZeroColumn(self.name, self.start_timestamp, self.end_timestamp).get_column_df()

    def get_liabilities_delta(self):
        return ZeroColumn(self.name, self.start_timestamp, self.end_timestamp).get_column_df()


class SimpleIncomeStream(FinanceObject):
    def __init__(self, name, start_timestamp, end_timestamp, income_amount):
        super(SimpleIncomeStream, self).__init__()
        self.add_column_object(IncomeColumn(name, start_timestamp, end_timestamp, income_amount))


class SpecifiedIncomeStream(FinanceObject):
    def __init__(self, name, csv_path, **kwargs):
        super(SpecifiedIncomeStream, self).__init__()
        self.income_df = pd.read_csv(csv_path)
        self.start_timestamp = min(self.income_df['timestamp'])
        self.end_timestamp = max(self.income_df['timestamp'])
        self.income_col = self.income_df['income'].astype(float)
        if "percentage" in kwargs:
            self.income_col = self.income_df['income'].astype(float) * kwargs["percentage"]
        self.add_column_object(IncomeColumn(name, self.start_timestamp, self.end_timestamp, self.income_col))
