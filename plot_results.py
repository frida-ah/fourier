import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

product = "asperge"
pdf = pd.read_csv(f"data/{product}_all_years.csv", sep=";")
pdf["date"] = pd.to_datetime(pdf["date"], format="%Y-%m-%d")
pdf = pdf.set_index("date")

fig, axs = plt.subplots(ncols=1, figsize=(30, 5))
sns.lineplot(data=pdf, x="date", y="searches")
plt.show()
