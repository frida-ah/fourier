import pandas as pd
import math
from cmath import phase

import numpy as np
import pandas as pd
from scipy import fft
from scipy import signal as sig
from sklearn.linear_model import LinearRegression


def add_trend_term(pdf):
    pdf["ind_trend_num"] = pdf.apply(lambda row: row.name + 1, axis=1)
    return pdf


def add_fourier_seasonality_term(pdf, column_name, period_min, period_max, apply_linear_regression):
    # Performs fourier transformation
    fft_output = fft.fft(pdf[column_name].to_numpy())
    amplitude = np.abs(fft_output)
    freq = fft.fftfreq(len(pdf[column_name].to_numpy()))

    mask = freq >= 0
    freq = freq[mask]
    amplitude = amplitude[mask]

    # determine peaks
    peaks = sig.find_peaks(amplitude[freq >= 0])[0]
    peak_freq = freq[peaks]
    peak_amplitude = amplitude[peaks]

    # Create dataframe containing necessary parameters
    fourier_output = pd.DataFrame()
    fourier_output["index"] = peaks
    fourier_output["freq"] = peak_freq
    fourier_output["amplitude"] = peak_amplitude
    fourier_output["period"] = 1 / peak_freq
    fourier_output["fft"] = fft_output[peaks]
    fourier_output["amplitude"] = fourier_output.fft.apply(lambda z: np.abs(z))
    fourier_output["phase"] = fourier_output.fft.apply(lambda z: phase(z))

    N = len(pdf.index)
    fourier_output["amplitude"] = fourier_output["amplitude"] / N

    fourier_output = fourier_output.sort_values("amplitude", ascending=False)
    fourier_output = fourier_output[fourier_output["period"] >= period_min]
    fourier_output = fourier_output[fourier_output["period"] <= period_max]

    # Turn our dataframe into a dictionary for easy lookup
    fourier_output_dict = fourier_output.to_dict("index")
    pdf_temp = pdf[["ind_trend_num"]]

    lst_periods = fourier_output["period"].to_list()
    lst_periods = [int(round(val, 0)) for val in lst_periods]

    for key in fourier_output_dict.keys():
        a = fourier_output_dict[key]["amplitude"]
        w = 2 * math.pi * fourier_output_dict[key]["freq"]
        p = fourier_output_dict[key]["phase"]
        pdf_temp[key] = pdf_temp["ind_trend_num"].apply(lambda t: a * math.cos(w * t + p))

    pdf_temp["FT_All"] = 0
    for column in list(fourier_output.index):
        pdf_temp["FT_All"] = pdf_temp["FT_All"] + pdf_temp[column]

    pdf["ind_seasonality_num"] = pdf_temp["FT_All"].astype(float)
    pdf["ind_seasonality_num"] = pdf["ind_seasonality_num"].round(4)

    if apply_linear_regression:
        predictors = ["ind_trend_num", "ind_seasonality_num"]
        X = pdf[predictors]
        y = pdf["sales"]

        X_predict = pdf[predictors]

        # Initialise and fit model
        lm = LinearRegression()
        model = lm.fit(X, y)

        # Forecast baseline for entire dataset
        pdf["ind_baseline_num"] = model.predict(X_predict)
        pdf["ind_baseline_num"] = pdf["ind_baseline_num"].round(4)
    return (fourier_output, pdf)


def create_plots(pdf, period_min, period_max, apply_linear_regression):
    import matplotlib.pyplot as plt
    import seaborn as sns

    pdf = pdf.reset_index()
    pdf = add_trend_term(pdf=pdf)

    (fourier_output, pdf) = add_fourier_seasonality_term(
        pdf,
        column_name="sales",
        period_min=period_min,
        period_max=period_max,
        apply_linear_regression=apply_linear_regression,
    )
    print(pdf)

    pdf = pdf.set_index("date")
    fig, axs = plt.subplots(ncols=1, figsize=(30, 5))
    sns.lineplot(data=pdf, x="date", y="sales")
    ax2 = axs.twinx()
    if apply_linear_regression:
        sns.lineplot(x="date", y="ind_baseline_num", data=pdf, ax=ax2, color="blue")
    else:
        sns.lineplot(x="date", y="ind_seasonality_num", data=pdf, ax=ax2, color="blue")

    plt.show()


product = "FOODS_3_586"
create_plots(
    pdf=pd.read_csv(f"product_{product}_one_year.csv", sep=","),
    period_min=60,
    period_max=80,
    apply_linear_regression=False,
)
