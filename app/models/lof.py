import pandas as pd
from pyod.models.lof import LOF

from app.onlinelearning.utils import get_last_version_model_river


def get_column_outliers(df, metric):
    model = get_last_version_model_river(f"lof_{metric}")

    scores = []
    print(len(df.to_dict(orient='records')))
    i=0
    for dict in df.to_dict(orient='records'):
        i=i+1
        print(i)
        score = model.score_one(dict)
        scores.append(score)

    ucl = pd.DataFrame(scores).quantile(0.97)

    df['anomaly'] = pd.DataFrame(scores, index=df.index) > ucl
    df['anomaly'] = df['anomaly'].astype(bool)
    # clf = LOF(n_neighbors=300, contamination=0.05)
    #
    # X = df[['value']].values.reshape(-1, 1)
    # clf.fit(X)
    #
    # y_pred = clf.predict(X)
    # df['anomaly'] = y_pred.tolist()
    # df['anomaly'] = df['anomaly'].astype(bool)
    #
    # with pd.option_context("display.max_rows", 1000):
    #     print(df)

    return df


def add_anomaly_column(df, metric):
    df = get_column_outliers(df, metric)

    return df
