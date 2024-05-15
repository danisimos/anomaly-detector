

import app.models.autoencoder as autoencoder
import app.models.iqr as iqr
import app.models.isolation_forest as isolation_forest
import app.models.kmeans as kmeans
import app.models.knn as knn
import app.models.lof as lof
import app.models.lstm as lstm
import app.models.ocsvm as ocsvm
import app.models.transformer as transformer

methods = {
    'IQR': iqr.add_anomaly_column,
    'Autoencoder': autoencoder.add_anomaly_column,
    'LSTM': lstm.add_anomaly_column,
    'OCSVM': ocsvm.add_anomaly_column,
    'IsolationForest': isolation_forest.add_anomaly_column,
    'KNN': knn.add_anomaly_column,
    'LOF': lof.add_anomaly_column,
    'KMEANS': kmeans.add_anomaly_column,
    'Transformer': transformer.add_anomaly_column
}


def find_anomalies_from_df(df, anomaly_model, metric):
    df = methods[anomaly_model](df, metric)
    return df

