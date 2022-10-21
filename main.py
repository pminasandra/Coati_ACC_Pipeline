# Pranav Minasandra
# pminasandra.github.io
# September 06, 2022

import glob
import os
import os.path

import matplotlib.pyplot as plt
import pandas as pd
import sklearn.ensemble
import sklearn.metrics
import sklearn.model_selection
import sklearn.neighbors
import sklearn.svm

import auditreading
import config
import utilities


# First read all available audit data
audit_data = pd.concat(auditreading.read_all_audits())
audit_data.sort_values(by='datetime', ignore_index = True)

# Read features and merge them
ft_data = pd.read_csv(f"{config.DATA_DIR}features/tag9478_acc.csv")
ft_data['datetime'] = pd.to_datetime(ft_data['datetime'])

df = ft_data.merge(audit_data, how="inner", on="datetime")
states = list(df['state'])
combined_states = [config.REDUCED_STATE[state] for state in states]
df['state'] = pd.Series(combined_states)

# Sort data into training and test dataframes
df_train, df_test = sklearn.model_selection.train_test_split(df, test_size=0.2)
df_train.sort_values(by='datetime', ignore_index = True)
df_test.sort_values(by='datetime', ignore_index = True)

# Set up classifiers
NearestNeighborClassifier = sklearn.neighbors.KNeighborsClassifier(10)
SVMClassifier = sklearn.svm.SVC(gamma='scale')
RandomForestClassifier = sklearn.ensemble.RandomForestClassifier()
ListOfClassifiers = [NearestNeighborClassifier, SVMClassifier, RandomForestClassifier]

# Train all classifiers
for Classifier in ListOfClassifiers:
    Classifier.fit(df_train[df_train.columns[1:len(df_train.columns)-1]], df_train['state'])

# Test all classifiers
NearestNeighborClassifier_pred = NearestNeighborClassifier.predict(df_test[df_test.columns[1:len(df_train.columns)-1]])
SVMClassifier_pred = SVMClassifier.predict(df_test[df_test.columns[1:len(df_train.columns)-1]])
RandomForestClassifier_pred = RandomForestClassifier.predict(df_test[df_test.columns[1:len(df_train.columns)-1]])

NearestNeighborClassifier_a = sklearn.metrics.accuracy_score(df_test['state'], NearestNeighborClassifier_pred, normalize=True)
SVMClassifier_a = sklearn.metrics.accuracy_score(df_test['state'], SVMClassifier_pred, normalize=True)
RandomForestClassifier_a = sklearn.metrics.accuracy_score(df_test['state'], RandomForestClassifier_pred, normalize=True)

print("Classifier\t\t|\tAccuracy")
print()
print(f"k-NN Classifier:\t|\t{NearestNeighborClassifier_a:.3f}")
print(f"SVM Classifier:\t\t|\t{SVMClassifier_a:.3f}")
print(f"RF Classifier:\t\t|\t{RandomForestClassifier_a:.3f}")

display = sklearn.metrics.ConfusionMatrixDisplay.from_predictions(df_test['state'], RandomForestClassifier_pred)
utilities.saveimg(plt, "RF_initial_confusion_matrix")
