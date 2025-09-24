# src/train_ids.py
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
df = pd.read_csv('data/features.csv', parse_dates=['timestamp'])
X = df[['speed_kmph','turn_angle','ang_vel','hour_sin','hour_cos']].fillna(0)
scaler = StandardScaler().fit(X)
Xs = scaler.transform(X)
model = IsolationForest(n_estimators=200, contamination=0.02, random_state=42)
model.fit(Xs)
joblib.dump(model, 'models/isolation_forest.joblib')
joblib.dump(scaler, 'models/scaler.joblib')
print("Saved model and scaler")
