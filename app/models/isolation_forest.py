import pandas as pd
from pyod.models.iforest import IForest


def get_column_outliers(df):
    clf = IForest(contamination=float(0.01))
    X = df[['value']].values.reshape(-1, 1)
    clf.fit(X)


    # model = load('app/models/h5models/if.joblib')

    y_pred = clf.predict(X)
    df['anomaly'] = y_pred.tolist()
    df['anomaly'] = df['anomaly'].astype(bool)

    # with pd.option_context("display.max_rows", 1000):
    #     print(df)

    return df


def add_anomaly_column(df, metric):
    df = get_column_outliers(df)

    return df
