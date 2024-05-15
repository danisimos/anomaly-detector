import mlflow.pyfunc

from app import get_prometheus_metrics, get_df_from_prometheus_metrics
from app.models import lstm
from app.models import autoencoder
from app.models import ocsvm
from app.onlinelearning.utils import update_model, get_last_version_model_keras, create_registry_model_river, \
    get_last_version_model_river
from config import get_config

cfg = get_config()
mlflow.set_tracking_uri("http://localhost:5000/")
mlflow.set_experiment("model_registry")

methods_partial_fit = {
    # 'lstm': lstm.do_partial_fit,
    # 'autoencoder': autoencoder.do_partial_fit,
    'ocsvm': ocsvm.do_partial_fit
}
methods_model_type_loading = {
    'lstm': get_last_version_model_keras,
    'autoencoder': get_last_version_model_keras,
    'ocsvm': get_last_version_model_river
}
model_type = {
    'lstm': 'keras',
    'autoencoder': 'keras',
    'ocsvm': 'river'
}
metrics = ['cpu', 'memory']



def update_models():
    dfs = {
        'cpu': get_df_from_prometheus_metrics(
            get_prometheus_metrics(start_time='1h', end_time='now', prometheus_url=cfg.PROMETHEUS_URL, metric='cpu')
        ),
        'memory': get_df_from_prometheus_metrics(
            get_prometheus_metrics(start_time='1h', end_time='now', prometheus_url=cfg.PROMETHEUS_URL, metric='memory')
        )
    }

    for method in methods_partial_fit.keys():
        for metric in metrics:
            model_name = f"{method}_{metric}"
            print(model_name)

            model = methods_model_type_loading[method](model_name)
            print('partial fitting')
            model = methods_partial_fit[method](model, dfs[metric])

            print('updating')

            update_model(model=model, model_name=model_name, model_type=model_type[method])


if __name__ == '__main__':
    update_models()
    # dfs = {
    #     'cpu': get_df_from_prometheus_metrics(
    #         get_prometheus_metrics(start_time='1h', end_time='now', prometheus_url=cfg.PROMETHEUS_URL, metric='cpu')
    #     ),
    #     'memory': get_df_from_prometheus_metrics(
    #         get_prometheus_metrics(start_time='1h', end_time='now', prometheus_url=cfg.PROMETHEUS_URL, metric='memory')
    #     )
    # }
    # #
    # # create_registry_model_river('ocsvm', 'memory', dfs['memory'])
    # # create_registry_model_river('ocsvm', 'cpu', dfs['cpu'])
    #
    # create_registry_model_river('lof', 'cpu', dfs['cpu'])
    # create_registry_model_river('lof', 'memory', dfs['memory'])
