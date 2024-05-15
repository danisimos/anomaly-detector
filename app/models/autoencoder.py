import os

import mlflow.client
import numpy as np
import pandas as pd

from app.onlinelearning.utils import get_last_version_model_keras

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

models = {
    'cpu': 'app/models/h5models/model_autoencoder_collected_cpu_usage (1).h5',
    'memory': 'app/models/h5models/model_autoencoder_collected_ram_usage.h5'
}


def get_column_outliers(df, metric):
    # StSc = StandardScaler()
    # StSc.fit(df[['value']])
    # df_sc = StSc.transform(df[['value']])

    model = get_last_version_model_keras(f"autoencoder_{metric}")
    # model = load_model(models[metric])

    pred = model.predict(df[['value']])
    pred_residuals = df[['value']] - np.abs(pred)
    ucl = pd.DataFrame(pred_residuals).abs().sum(axis=1).quantile(0.90)

    df['anomaly'] = pd.DataFrame(pred_residuals, index=df.index).abs().sum(axis=1) > ucl

    df_clone = df.copy()

    df_clone['pred'] = pred

    with pd.option_context("display.max_rows", 1000):
        print(ucl)
        print(df_clone)
    print(df_clone.loc[df_clone.anomaly])

    return df


def do_partial_fit(model, df):
    model.train_on_batch(x=df[['value']], y=df[['value']])

    return model


def add_anomaly_column(df, metric):
    df = get_column_outliers(df, metric)

    return df
