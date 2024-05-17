from datetime import datetime as dt

import pandas as pd
from prometheus_api_client import PrometheusConnect
from prometheus_api_client.utils import parse_datetime
from app.models import find_anomalies_from_df

from config import get_config

cfg = get_config()
queries = {
    'cpu': cfg.PROMETHEUS_QUERY_CPU,
    'memory': cfg.PROMETHEUS_QUERY_MEMORY
}


def get_metrics(start_time, end_time, prometheus_url, anomaly_model, ajax_request_json, metric):
    prometheus_metrics = get_prometheus_metrics(start_time=start_time, end_time=end_time, prometheus_url=prometheus_url,
                                                metric=metric)
    df_new_interval = get_df_from_prometheus_metrics(prometheus_metrics)

    time, values = get_time_series_from_df(df_new_interval)
    time_anomaly = []
    values_anomaly = []

    if anomaly_model is not None:
        df_all = get_df_from_ajax_json(ajax_request_json)
        df_all = pd.concat([df_all, df_new_interval])

        df_all = find_anomalies_from_df(df_all, anomaly_model, metric)

        t, v, ta, va = get_anomaly_time_series_from_df(df_all)
        if len(ta) > 0 and ta[-1] == time[0]:
            time_anomaly.append(time[0])
            values_anomaly.append(values[0])

    return time, values, time_anomaly, values_anomaly


def get_prometheus_metrics(start_time, end_time, prometheus_url, metric):
    prom = PrometheusConnect(url='http://' + prometheus_url, disable_ssl=True)

    step = 30#*60 if (str(start_time).endswith('d')) else 10
    start_time = parse_datetime(start_time)
    end_time = parse_datetime(end_time)


    result = prom.custom_query_range(
        query=queries[metric],
        start_time=start_time,
        end_time=end_time,
        step=str(step)
    )

    return result


def get_df_from_prometheus_metrics(prometheus_data_json):
    df = pd.DataFrame(prometheus_data_json[0]['values'])
    df.columns = ['time', 'value']
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['time'] = [dt.fromtimestamp(x) for x in df['time']]
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)

    return df


def get_df_from_ajax_json(data_json):
    df = pd.DataFrame({'time': data_json['time'], 'value': data_json['values']})
    df.columns = ['time', 'value']
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)

    return df


def get_anomaly_time_series_from_df(df):
    anomalies = df.loc[df.anomaly, [df.columns[0]]]

    return (
        df.index.astype(str).tolist(),
        df.iloc[:, 0].values.tolist(),
        anomalies.index.astype(str).tolist(),
        anomalies.iloc[:, 0].values.tolist()
    )


def get_time_series_from_df(df):
    return (
        df.index.astype(str).tolist(),
        df.iloc[:, 0].values.tolist()
    )


def check_anomaly_now(timeframe, anomaly_model, prometheus_url):
    df_cpu = get_df_from_prometheus_metrics(
        get_prometheus_metrics(timeframe, 'now', prometheus_url, 'cpu')
    )
    df_memory = get_df_from_prometheus_metrics(
        get_prometheus_metrics(timeframe, 'now', prometheus_url, 'memory')
    )


    cpu_anomaly = find_anomalies_from_df(df_cpu, anomaly_model, 'cpu')['anomaly'].values
    memory_anomaly = find_anomalies_from_df(df_memory, anomaly_model, 'memory')['anomaly'].values

    result = {'cpu': any(cpu_anomaly[-31:]) == True,
              'memory': any(memory_anomaly[-31:]) == True}

    return result
