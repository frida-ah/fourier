import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

product = "FOODS_3_555"
pdf = pd.read_csv(f"product_{product}_one_year.csv", sep=",")

pdf = pdf.set_index("date")
fig, axs = plt.subplots(ncols=1, figsize=(30, 5))
sns.lineplot(data=pdf, x="date", y="sales")
plt.show()
