import os

import keras
import mlflow
import numpy as np
import pandas as pd


import config
from app.onlinelearning.utils import get_last_version_model_keras

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

models = {
    'cpu': 'app/models/h5models/model_lstm_collected_cpu_usage.h5 (3)',
    'memory': 'app/models/h5models/model_lstm_collected_ram_usage.h5'
}
cfg = config.get_config()
# client = mlflow.client.MlflowClient()

# def get_model(method, metric):
#     model_name = f"{method}_{metric}"
#
#     model_run_id = client.get_latest_versions(name=model_name, stages=['Production'])[0].run_id
#     model_uri = f"runs:/{model_run_id}/{model_name}"
#     model_loaded = mlflow.tensorflow.load_model(model_uri)
#
#     return model_loaded


def get_column_outliers(df, metric):
    seq_size = 30
    X, Y = to_sequences(x=df[['value']], seq_size=seq_size)

    model = get_last_version_model_keras(f"lstm_{metric}")
    # if metric == 'cpu':
    #     model = get_model('lstm')
    # elif metric == 'memory':
    # model = keras.models.load_model(models[metric])

    pred = model.predict(X)

    df_sliced = df.iloc[seq_size:]

    pred_residuals = df_sliced - np.abs(pred)

    ucl = pd.DataFrame(pred_residuals).abs().sum(axis=1).quantile(0.985)
    anomalies = pd.DataFrame(pred_residuals, index=df_sliced.index).abs().sum(axis=1) > ucl


    for i in range(0, seq_size):
        anomalies = np.insert(anomalies, 0, False, axis=0)
        pred = np.insert(pred, 0, 0.6, axis=0)

    df['anomaly'] = anomalies

    df_clone = df.copy()

    df_clone['pred'] = pred

    # with pd.option_context("display.max_rows", 1000):
    #     print(ucl)
    #     print(df_clone)

    return df


def to_sequences(x, y=None, seq_size=1):
    x_values = []
    y_values = []

    for i in range(len(x) - seq_size):
        x_values.append(x.iloc[i:(i + seq_size)].values)
        if y is not None:
            y_values.append(y.iloc[i + seq_size])

    return np.array(x_values), np.array(y_values)


def do_partial_fit(model, df):

    seq_size = 30
    X, Y = to_sequences(df[['value']], df['value'], seq_size=seq_size)

    model.train_on_batch(x=X, y=Y)

    return model


def add_anomaly_column(df, metric):
    df = get_column_outliers(df, metric)

    return df
