import pandas as pd

from app.onlinelearning.utils import get_last_version_model_river


def get_column_outliers(df, metric):
    model = get_last_version_model_river(f"ocsvm_{metric}")

    scores = []
    for dict in df.to_dict(orient='records'):
        score = model.score_one(dict)
        scores.append(score)

    ucl = pd.DataFrame(scores).quantile(0.99)

    df['anomaly'] = pd.DataFrame(scores, index=df.index) > ucl
    df['anomaly'] = df['anomaly'].astype(bool)

    # outliers_fraction = 0.05
    # clf = OCSVM(kernel='rbf', degree=3, gamma='auto', coef0=0.0, tol=0.001, nu=0.5,
    #                                     shrinking=True, cache_size=200, verbose=True, max_iter=-1,
    #                                     contamination=outliers_fraction)
    #
    #
    # X = df[['value']].values.reshape(-1, 1)
    #
    # if(metric == 'memory'):
    #     StSc = StandardScaler()
    #     StSc.fit(df[['value']])
    #
    #     df_sc = StSc.transform(df[['value']])
    #     X = df_sc
    #
    # clf.fit(X)
    #
    #
    # y_pred = clf.predict(X)
    # df['anomaly'] = y_pred.tolist()
    # df['anomaly'] = df['anomaly'].astype(bool)

    return df


def do_partial_fit(model, df):
    for dict in df.to_dict(orient='records'):
        model.learn_one(dict)

    return model


def add_anomaly_column(df, metric):
    df = get_column_outliers(df, metric)

    return df
