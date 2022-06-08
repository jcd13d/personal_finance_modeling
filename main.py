import json
# from FinanceTools.FixedIncomes import FixedIncome, OneTimePayment, TaxedSalary, Salary, MonthlyExpense, OneTimeGift
import os
import matplotlib.pyplot as plt
import matplotlib

from FinancesTools.FinancesObjects import FinancesBuilder
from FinancesTools.Income import SimpleIncomeStream, SpecifiedIncomeStream
from FinancesTools.Loans import Loan
from FinancesTools.Assets import CashFlowAsset
from datetime import datetime


def builder_pipeline(builder, config):

    # if "fixed_incomes" in config:
    #     for fi in config['fixed_incomes']:
    #         builder.add_object(FixedIncome(**fi))
    #
    # if "salaries" in config:
    #     for s in config['salaries']:
    #         builder.add_object(Salary(**s))
    #
    # if "taxed_salaries" in config:
    #     for s in config['taxed_salaries']:
    #         builder.add_object(TaxedSalary(**s))
    #
    # if "one_time_payments" in config:
    #     for otp in config['one_time_payments']:
    #         builder.add_object(OneTimePayment(**otp))
    #
    # if "one_time_gifts" in config:
    #     for cfg in config['one_time_gifts']:
    #         builder.add_object(OneTimeGift(**cfg))
    #
    # if "monthly_expenses" in config:
    #     for me in config['monthly_expenses']:
    #         builder.add_object(MonthlyExpense(**me))
    #

    if "loans" in config:
        for ln in config['loans']:
            builder.add_finance_object(Loan(**ln))

    if "assets" in config:
        for cfg in config['assets']:
            builder.add_finance_object(CashFlowAsset(**cfg))

    if "incomes" in config:
        for cfg in config['incomes']:
            if "type" in cfg:
                if cfg['type'] == "manual_schedule":
                    builder.add_finance_object(SpecifiedIncomeStream(**cfg))
            else:
                builder.add_finance_object(SimpleIncomeStream(**cfg))

    return builder


def plots(df, out_dir, xrange=None, yrange=None, figsize=None):
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(df.index, df['NW'], label="Net Worth", marker="o")
    ax.plot(df.index, df['Cash Balance'], label="Cash Balance", marker="o")
    ax.plot(df.index, df['Assets'], label="Assets", marker="o")
    ax.plot(df.index, df['Liabilities'], label="Liabilities", marker="o")
    plt.xticks([i for i in df.index if i % 2 == 0], [x for i, x in enumerate(df['timestamp']) if i % 2 == 0], rotation=45)
    plt.hlines(y=0, xmin=min(df.index), xmax=max(df.index), color="black", linestyles="--")
    plt.xlim(xrange)
    plt.ylim(yrange)
    plt.xlabel("months")
    plt.ylabel("Dollars")
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "nw_plot.jpg"))


if __name__ == '__main__':
    config_loc = "config.json"
    time = datetime.today().strftime('%Y%m%d%H%M%S')
    out_path = f"{time}.csv"
    executions_path = "executions"
    executions_path = os.path.join(executions_path, time)
    os.mkdir(executions_path)
    out_path = os.path.join(executions_path, out_path)

    with open(config_loc, "r") as f:
        config = json.load(f)

    with open(os.path.join(executions_path, "config.json"), "w") as f:
        json.dump(config, f, indent=4)

    builder = FinancesBuilder()

    builder = builder_pipeline(builder, config)

    df = builder.generate_master_df()
    print("printing")
    print(df)
    plots(df, executions_path, **config['plotting'])
    print(executions_path)
    df.to_csv(out_path)
