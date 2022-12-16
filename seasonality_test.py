import pandas as pd
from scipy.stats import friedmanchisquare


def seasonality_test(input_data: pd.DataFrame, label_field: str) -> bool:
    input_data["year"] = pd.DatetimeIndex(input_data["date"]).year
    input_data["month"] = pd.DatetimeIndex(input_data["date"]).month

    transformations = {label_field: "mean"}

    input_data = input_data.groupby(["year", "month"]).agg(transformations)

    input_data.reset_index(inplace=True)

    min_year = input_data[input_data["month"] == 1]["year"].min()
    max_year = input_data[input_data["month"] == 12]["year"].max()
    print(f"Complete years from: {min_year} to {max_year}")
    input_data = input_data[(input_data["year"] >= min_year) & (input_data["year"] <= max_year)]

    year_values = [year for year in input_data["year"].unique()]

    number_of_years = len(year_values)

    input_data = input_data.pivot(index="month", columns="year", values=label_field)

    stat, p = friedmanchisquare(
        input_data[year_values[number_of_years - 3]],
        input_data[year_values[number_of_years - 2]],
        input_data[year_values[number_of_years - 1]],
    )

    print("Statistics=%.3f, p=%.3f" % (stat, p))
    # interpret
    alpha = 0.01
    if p > alpha:
        print("Same distributions (fail to reject H0)")
        season = True
    else:
        print("Different distributions (reject H0)")
        season = False
    return season


product = "FOODS_3_586"
pdf = pd.read_csv(f"product_{product}_all_years.csv", sep=",")
season = seasonality_test(input_data=pdf, label_field="sales")
print(f"Seasonality is: {season}")

# Complete years from: 2011 to 2015
# Statistics=3.500, p=0.174
# Same distributions (fail to reject H0)
# Seasonality is: True
