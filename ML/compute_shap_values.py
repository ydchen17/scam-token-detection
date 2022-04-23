import matplotlib.pyplot as plt
import shap
import xgboost as xgb
import pandas as pd

X = pd.read_csv("features24h.csv").drop(['pool_address', 'token_address'], axis=1)
X, y = X.drop("label", axis=1), X['label']

model = xgb.XGBClassifier()
model.fit(X, y)
explainer = shap.Explainer(model)
shap_values = explainer(X)

shap.plots.beeswarm(shap_values)
plt.show()
print(shap_values)