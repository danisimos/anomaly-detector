import io

import pandas as pd
import torch
from pyod.models.ocsvm import OCSVM
import pickle
from joblib import dump, load
from deepod.models.time_series import AnomalyTransformer


from sklearn.preprocessing import StandardScaler
from deepod.models.time_series import AnomalyTransformer

models = {
    'cpu': 'app/models/h5models/model_transformer_collected_cpu_usage (4).pkl',
    'memory': 'app/models/h5models/model_transformer_collected_ram_usage (3).pkl'
}

scalers = {
    'memory': 'app/models/h5models/scaler_transformer_ram.bin'
}

class CPU_Unpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == 'torch.storage' and name == '_load_from_bytes':
            return lambda b: torch.load(io.BytesIO(b), map_location='cpu')
        else:
            return super().find_class(module, name)

def get_column_outliers(df, metric):

    # model = pickle.load(open(models[metric], 'rb'), map)
    # print('loading model')
    model = CPU_Unpickler(open(models[metric], 'rb')).load()
    # model = AnomalyTransformer(device='cpu', epochs=3, lr=0.1, stride=1, seq_len=10)

    # print('end loading model')

    df_sc = df.copy()
    column_name = 'value'
    print('predicting model')
    if metric == 'memory':
        print('tmp skip')
        # scaler = load(scalers[metric])
        # df_sc.columns = ['ram_usage']
        # column_name = 'ram_usage'
        # df_sc['ram_usage'] = scaler.transform(df_sc[['ram_usage']])
    elif metric == 'cpu':
        df_sc['value'] = df_sc['value'] - 0.5

    # model.fit(df_sc[[column_name]])
    print(df_sc[[column_name]].values)
    y_pred = model.predict(df_sc[[column_name]].values)
    print('end predicting model')
    df['anomaly'] = y_pred.tolist()
    df['anomaly'] = df['anomaly'].astype(bool)

    with pd.option_context("display.max_rows", 1000):
        print(df)

    return df


def add_anomaly_column(df, metric):
    df = get_column_outliers(df, metric)

    return df
