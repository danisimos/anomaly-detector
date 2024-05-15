import pandas as pd


def outlier_std(data, col, threshold=1.5):
    mean = data[col].mean()
    std = data[col].std()
    up_bound = mean + threshold * std
    low_bound = mean - threshold * std

    # интерквантильный размах
    IQR = data[col].quantile(0.75) - data[col].quantile(0.25)

    # насколько размахов отступать
    up_bound_iqr = data[col].quantile(0.75) + (IQR * threshold)
    low_bound_iqr = data[col].quantile(0.25) - (IQR * threshold)

    anomalies = pd.concat(
        [(data[col] > up_bound) | (data[col] > up_bound_iqr), (data[col] < low_bound) | (data[col] < low_bound_iqr)],
        axis=1).any(axis=1)
    return anomalies, up_bound, low_bound, up_bound_iqr, low_bound_iqr, mean, std


def get_column_outliers(data, columns=None, function=outlier_std, threshold=3):
    print('duplicates:')
    print(data[data.index.duplicated(keep=False)])
    if columns:
        columns_to_check = columns
    else:
        columns_to_check = data.columns

    outliers = pd.Series(data=[False] * len(data), index=data.index, name='is_outlier')
    comparison_table = {}
    for column in columns_to_check:
        anomalies, upper_bound, lower_bound, up_bound_iqr, low_bound_iqr, mean, std = function(data, column,
                                                                                               threshold=threshold)
        comparison_table[column] = [upper_bound, lower_bound, up_bound_iqr, low_bound_iqr, mean, std, sum(anomalies),
                                    100 * sum(anomalies) / len(anomalies)]
        print(anomalies)
        outliers[anomalies[anomalies].index] = True

    comparison_table = pd.DataFrame(comparison_table).T
    comparison_table.columns = ['upper_bound', 'lower_bound', 'up_bound_iqr', 'low_bound_iqr', 'mean', 'std',
                                'anomalies_count', 'anomalies_percentage']

    return comparison_table, outliers


def add_anomaly_column(df, metric):
    comparison_table, outliers = get_column_outliers(df)
    df['anomaly'] = outliers

    return df
