import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score, precision_score, accuracy_score, recall_score, balanced_accuracy_score

df = pd.read_csv("breast_dataset.csv")

labelencoder = LabelEncoder()
df.iloc[:,-1] = labelencoder.fit_transform(df.iloc[:,-1].values)
print(df.head())
X = df.iloc[:,:-1]
y = df['diagnosis']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.35, random_state = 7)
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
tuned_params = {'C': [0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000], 'penalty': ['l1', 'l2']}
model = GridSearchCV(LogisticRegression(), tuned_params, scoring = 'roc_auc', n_jobs=-1)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

y_train_pred = model.predict(X_train)

from sklearn.metrics import roc_auc_score
print(model.score(X_train,y_train))

import pickle
pickle.dump(model,open('breastmodel.pkl','wb'))