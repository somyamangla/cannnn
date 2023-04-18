import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from sklearn.metrics import accuracy_score
warnings.filterwarnings('ignore')

df = pd.read_csv("CERVICAL FEATURES SELECTED DATA.csv")
df.head() ##this returns the first five rows of the dataset


df.shape ##returns the no. of rows and columns
df.dtypes
df.describe
df.isnull().sum() ##check for null values

for x in df.columns:
    df[x].replace("?",np.nan,inplace=True)

def imputation_null_value(df):
    for x in  df.columns:
        value =df[x].mode(dropna=True).loc[0]
        df[x].fillna(value,inplace=True)
imputation_null_value(df)

df.duplicated().any() ##check for duplicate values

X= df.iloc[:,:-1]
y= df['Biopsy']

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= 0.2, random_state=0)

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
x_train = scaler.fit_transform(X_train)
x_test = scaler.transform(X_test)

from xgboost import XGBClassifier
classifier = XGBClassifier()
classifier.fit(x_train, y_train)

y_pred = classifier.predict(x_test)
acc7 = accuracy_score(y_test, y_pred)

import pickle
pickle.dump(classifier, open('cervicalmodel.pkl', 'wb'))