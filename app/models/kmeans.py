import numpy as np
import pandas as pd
from numpy import percentile
from pyod.models.ocsvm import OCSVM
from sklearn.cluster import KMeans


def get_column_outliers(df):
    clf = KMeans(n_clusters=4)

    X = df[['value']]
    clf.fit(X)

    cluster_pred = clf.predict(X)
    dist = getDistanceByPoint(X, clf)
    threshold = percentile(dist, 95)
    is_outlier = (dist >= threshold) * 1

    is_outlier_df = pd.DataFrame(is_outlier)
    is_outlier_df.set_index(df.index)
    df['anomaly'] = is_outlier_df.iloc[:, 0].values
    df['anomaly'] = df['anomaly'].astype(bool)

    with pd.option_context("display.max_rows", 1000):
        print(df)

    return df


def getDistanceByPoint(data, model):
    distance = pd.Series()

    for i in range(0, len(data)):
        Xa = np.array(data.iloc[i])
        Xb = model.cluster_centers_[model.labels_[i] - 1]
        distance.at[i] = np.linalg.norm(Xa - Xb)
    return distance


def add_anomaly_column(df, metric):
    df = get_column_outliers(df)

    return df
