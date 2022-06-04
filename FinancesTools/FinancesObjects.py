import pandas as pd


class ColumnObject:
    def __init__(self, name, start_timestamp, end_timestamp):
        self.name = name
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.column_df = None

    @staticmethod
    def timestamp_check(timestamp):
        month = timestamp % 100
        assert ((month >= 1) and (month <= 12))

    @staticmethod
    def build_index(start_time, end_time):
        ColumnObject.timestamp_check(start_time)
        ColumnObject.timestamp_check(end_time)
        stamps = []
        current_stamp = start_time
        while current_stamp <= end_time:
            stamps.append(current_stamp)
            if current_stamp % 100 == 12:
                current_stamp = current_stamp + 89
            else:
                current_stamp += 1
        return pd.DataFrame({"timestamp": stamps})

    def add_to_col(self, df):
        """
        Merge dataframes and return just the dataframe with the original column
        """
        new_col_name = df.columns.to_list()
        new_col_name.remove("timestamp")
        new_col_name = new_col_name[0]
        temp_df = self.get_column_df().merge(df, how="left", on="timestamp").fillna(0)
        temp_df[self.name] = temp_df[self.name] + temp_df[new_col_name]
        self.column_df = temp_df[["timestamp", self.name]]

    def get_net_cash_delta(self):
        raise NotImplemented("implement add to net cash behavior!")

    def get_assets_delta(self):
        raise NotImplemented("implement add to assets behavior!")

    def get_liabilities_delta(self):
        raise NotImplemented("implement add to liabilities behavior!")

    def get_column_df(self):
        raise NotImplemented("get column behavior must be implemented")


class SpecifiedColumn(ColumnObject):
    def __init__(self, name, start_timestamp, end_timestamp, column):
        super(SpecifiedColumn, self).__init__(name, start_timestamp, end_timestamp)
        self.column = column

    def get_column_df(self):
        df = self.build_index(self.start_timestamp, self.end_timestamp)
        df[self.name] = self.column
        return df

    def get_net_cash_delta(self):
        return ZeroColumn(self.name, self.start_timestamp, self.end_timestamp).get_column_df()

    def get_assets_delta(self):
        return ZeroColumn(self.name, self.start_timestamp, self.end_timestamp).get_column_df()

    def get_liabilities_delta(self):
        return ZeroColumn(self.name, self.start_timestamp, self.end_timestamp).get_column_df()



class ZeroColumn(ColumnObject):
    def __init__(self, name, start_timestamp, end_timestamp):
        super(ZeroColumn, self).__init__(name, start_timestamp, end_timestamp)

    def get_net_cash_delta(self):
        return None

    def get_assets_delta(self):
        return None

    def get_liabilities_delta(self):
        return None

    def get_column_df(self):

        if self.column_df is None:
            df = self.build_index(self.start_timestamp, self.end_timestamp)
            df[self.name] = 0
            self.column_df = df
        else:
            df = self.column_df

        return df


class FinanceObject:
    def __init__(self):
        self.columns = []

    def add_column_object(self, obj):
        self.columns.append(obj)

    def __iter__(self):
        return self.columns.__iter__()


class FinancesBuilder:
    def __init__(self):
        self.net_cash = None
        self.assets = None
        self.liabilities = None
        self.master_df = None
        self.objects = []
        self.min_timestamp = 999999
        self.max_timestamp = 000000

    def add_finance_object(self, obj):
        for col in obj:
            if col.start_timestamp < self.min_timestamp:
                self.min_timestamp = col.start_timestamp

            if col.end_timestamp > self.max_timestamp:
                self.max_timestamp = col.end_timestamp

        self.objects.append(obj)

    def merge_to_master(self, col):
        self.master_df.merge(col.get_column_df, how="left", on="timestamp")

    def generate_master_df(self):
        self.net_cash = ZeroColumn("net_cash", self.min_timestamp, self.max_timestamp)
        self.assets = ZeroColumn("net assets", self.min_timestamp, self.max_timestamp)
        self.liabilities = ZeroColumn("net liabilities", self.min_timestamp, self.max_timestamp)
        self.master_df = ColumnObject.build_index(self.min_timestamp, self.max_timestamp)
        print(f"Master DF: \n{self.master_df}")

        for obj in self.objects:
            for col in obj:
                print(col)
                self.master_df = self.master_df.merge(col.get_column_df(), how="left", on="timestamp").fillna(0)
                self.net_cash.add_to_col(col.get_net_cash_delta())
                self.assets.add_to_col(col.get_assets_delta())
                self.liabilities.add_to_col(col.get_liabilities_delta())

        # print(self.net_cash.get_column_df())
        # print(self.master_df)
        self.master_df = self.master_df.merge(self.net_cash.get_column_df(), how="left", on="timestamp").fillna(0)
        self.master_df = self.master_df.merge(self.assets.get_column_df(), how="left", on="timestamp").fillna(0)
        self.master_df = self.master_df.merge(self.liabilities.get_column_df(), how="left", on="timestamp").fillna(0)

        self.master_df['Cash Balance'] = self.master_df[self.net_cash.name].cumsum()
        self.master_df['Assets'] = self.master_df[self.assets.name].cumsum()
        self.master_df['Liabilities'] = self.master_df[self.liabilities.name].cumsum()
        self.master_df['NW'] = self.master_df['Cash Balance'] + self.master_df['Assets'] + self.master_df['Liabilities']

        return self.master_df


class Utility:

    @staticmethod
    def add_months_to_timestamp(timestamp, months):
        month = timestamp % 100
        year = timestamp // 100
        added = month + months
        new_month = added % 12
        years_passed = added // 12
        year = year + years_passed
        return year * 100 + new_month

    @staticmethod
    def subtract_months_from_timestamp(timestamp, months):
        # TODO not working

        month = timestamp % 100
        year = timestamp // 100
        # added = month + (12 - months)
        # new_month = added % 12
        # years_passed = added // 12
        # year = year - years_passed
        # return year * 100 + new_month
        ym = year * 12 - 1 + month
        nym = ym - months
        nm = nym % 12 + 1
        ny = nym // 12
        return ny * 100 + nm





