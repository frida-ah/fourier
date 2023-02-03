import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
from pytrends.request import TrendReq

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)


def create_date_filter(duration_filter, end_date, date_format="%Y-%m-%d"):
    end_date = datetime.datetime.strptime(end_date, date_format)
    end_date = end_date.date()
    start_date = end_date + relativedelta(months=-duration_filter)
    time_filter = str(start_date) + " " + str(end_date)
    return time_filter


def download_google_trends(gt_date_filter, list_keywords):
    pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25), retries=2, backoff_factor=0.1)

    pytrends.build_payload(kw_list=list_keywords, cat=71, timeframe=gt_date_filter, geo="NL")

    pdf_temp = None
    pdf_temp = pytrends.interest_over_time()

    pdf_temp.reset_index(inplace=True)
    pdf_temp = pdf_temp.reset_index(drop=True)

    pdf_temp["date"] = pdf_temp["date"].astype(str).str[:10]
    pdf_temp_long = pd.melt(
        pdf_temp,
        id_vars=["date", "isPartial"],
        value_vars=list_keywords,
        var_name=None,
        value_name="value",
        col_level=None,
    )
    pdf_searches = pdf_temp_long.rename(columns={"variable": "keyword", "value": "interest"})
    pdf_searches = pdf_searches.set_index("date")
    return pdf_searches


def create_test_data(keyword):
    google_trends_pdf = download_google_trends(create_date_filter(24, "2022-12-31"), list_keywords=[keyword])
    google_trends_pdf = google_trends_pdf.sort_index()
    timeseries_test = google_trends_pdf[["interest"]]
    timeseries_test = timeseries_test.rename(columns={"interest": "searches"})
    timeseries_test = timeseries_test.reset_index(drop=False)
    timeseries_test["date"] = timeseries_test["date"].astype("datetime64[ns]")
    return timeseries_test


def prepare_input_data(keyword):
    pdf = create_test_data(keyword)
    pdf_one_year = pdf.loc[pdf.loc[:, "date"] >= "2022-01-01"]
    pdf_one_year = pdf_one_year.set_index("date")
    pdf_one_year.to_csv(f"./data/{keyword}_one_year.csv", sep=";")
    pdf = pdf.set_index("date")
    pdf.to_csv(f"./data/{keyword}_all_years.csv", sep=";")
    return pdf


pdf = prepare_input_data(keyword="asperge")
print(pdf.tail(5))
