import pandas as pd
import numpy as np
import datetime

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)


def preprocess_data(product):
    pdf = pd.read_csv("sales_train_validation.csv", sep=",")
    dates = pd.read_csv("calendar.csv", sep=",")
    pdf = pdf.loc[(pdf["item_id"] == product)]
    pdf = pdf.drop(["id", "dept_id", "cat_id", "state_id"], axis=1)
    pdf = pdf.melt(id_vars=["item_id", "store_id"], var_name="day", value_name="sales")

    dates = dates.drop(
        [
            "event_name_1",
            "event_type_1",
            "event_name_2",
            "event_type_2",
            "snap_CA",
            "snap_TX",
            "snap_WI",
            "wm_yr_wk",
        ],
        axis=1,
    )
    pdf["day"] = pdf["day"].str.replace(r"d_", "").astype("int")
    dates["day"] = dates["d"].str.replace(r"d_", "").astype("int")

    pdf = pd.merge(pdf, dates, how="left", on="day")
    pdf = pdf.groupby(["date"]).agg({"sales": np.sum})
    pdf = pdf.reset_index()

    pdf["date"] = pdf["date"].astype("datetime64[ns]")
    pdf = pdf.sort_values(by="date")
    pdf = pdf.set_index("date")

    print(pdf.head(5))
    print(pdf.dtypes)

    pdf.to_csv(f"product_{product}_all_years.csv", sep=",")

    pdf = pdf.reset_index()
    pdf = pdf.loc[pdf.loc[:, "date"] >= datetime.datetime(2012, 1, 1)]
    pdf = pdf.loc[pdf.loc[:, "date"] < datetime.datetime(2013, 1, 1)]
    pdf = pdf.sort_values(by="date")
    pdf = pdf.set_index("date")

    pdf.to_csv(f"product_{product}_one_year.csv", sep=",")


# output daily data with date, sales
preprocess_data(product="FOODS_3_555")
