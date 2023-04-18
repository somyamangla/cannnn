import pickle
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

df = pd.read_csv("Indian_liver_patient.csv")

from sklearn import preprocessing 
my_label = preprocessing.LabelEncoder()   
df[ 'Gender' ]= my_label.fit_transform(df[ 'Gender' ])   
df

X = df.iloc[:,:-1]
y = df['Dataset']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.35, random_state = 42)
df.dtypes
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train),columns=X_train.columns)
X_train_scaled
X_test_scaled = pd.DataFrame(scaler.fit_transform(X_test),columns=X_test.columns)
X_test_scaled
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier()
X_train.fillna(X_train.mean(), inplace=True)
X_test.fillna(X_test.mean(), inplace=True)
model.fit(X_train,y_train)
from sklearn import model_selection , metrics
from sklearn.metrics import f1_score, precision_score, accuracy_score, recall_score, balanced_accuracy_score
prediction = model.predict(X_test)
prediction
accuracy = metrics.accuracy_score(y_test,prediction)
print(accuracy)

pickle.dump(model, open("livermodel.pkl","wb"))