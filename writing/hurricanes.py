import pandas as pd

path = r"/Users/jean-baptisteheurtel/Main/2022/02_university/02_thesis/Thesis/09_Writing/hurricanes.xlsx"

a = pd.read_excel(path)
a = a.set_index("Year")
a = a.iloc[100:, :]
a["Total_Hurricanes"] = a["Hurricanes"]
a["Hurricanes"] = a["Total_Hurricanes"]-a["Major Hurricanes"]

import statsmodels.api as sm
b = a.reset_index()
X = b.Year
Y = b['Major Hurricanes']
X = sm.add_constant(X)
model = sm.OLS(Y, X).fit()
summary = model.summary()
print(summary)

c = model.params


a["pred"] =  a.apply(lambda x: x.name*c["Year"] + c["const"], axis=1)
plt = a[['Hurricanes','Major Hurricanes']].plot(kind='bar', stacked=True)


