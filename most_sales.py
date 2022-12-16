import pandas as pd
import numpy as np

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

pdf = pd.read_csv("sales_train_validation.csv", sep=",")
dates = pd.read_csv("calendar.csv", sep=",")
pdf = pdf.drop(["id", "dept_id", "cat_id", "state_id"], axis=1)

pdf = pdf.melt(id_vars=["item_id", "store_id"], var_name="day", value_name="sales")
pdf = pdf.groupby(["item_id"]).agg({"sales": np.sum})
print(pdf.sort_values(by="sales", ascending=False).head(5))

#               sales
# item_id
# FOODS_3_090  1002529
# FOODS_3_586   920242
# FOODS_3_252   565299
# FOODS_3_555   491287
# FOODS_3_714   396172
