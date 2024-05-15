import os
import pickle

import keras
import mlflow
import mlflow.keras
import river.datasets
from mlflow import MlflowClient
from river import anomaly

from config import get_config

mlflow.set_tracking_uri("http://localhost:5000/")
mlflow.set_experiment("model_registry")
client = MlflowClient()
cfg = get_config()

online_learning_timeframe = '1h'

# models = {
#     'lstm': {
#         'cpu': '../models/h5models/model_lstm_collected_cpu_usage.h5 (3)',
#         'memory': '../models/h5models/model_lstm_collected_ram_usage.h5',
#         'partial_fit': 'kk'
#     },
#     'autoencoder': {
#         'cpu': '../models/h5models/model_autoencoder_collected_cpu_usage (1).h5',
#         'memory': '../models/h5models/model_autoencoder_collected_ram_usage.h5',
#         'partial_fit': 'tensorflow'
#     }
# }


class CustomRiverModel(mlflow.pyfunc.PythonModel):

    def __init__(self):
        self.model = None

    def load_context(self, context):
        with open(context.artifacts['model_path'], 'rb') as f:
            model = pickle.load(f)
            self.model = model

    def predict(self, context, input):
        if input is None:
            return self.model
        return self.model.score_one(input)

    @staticmethod
    def learn_one(self, input):
        return self.model.learn_one(input)


# def create_registry_model_keras(method, metric):
#     model_name = f"{method}_{metric}"
#
#     with mlflow.start_run(run_name=model_name) as run:
#         model = keras.models.load_model(models[method][metric])
#         mlflow.tensorflow.log_model(
#             model=model,
#             artifact_path=model_name,
#             keras_model_kwargs={"save_format": "h5"},
#             registered_model_name=model_name
#         )
#
#         versions = client.get_latest_versions(name=model_name)
#         version = versions[-1].version if len(versions) > 0 else 1
#         client.transition_model_version_stage(
#             name=model_name,
#             version=version,
#             stage='Production',
#             archive_existing_versions=True
#         )


def create_registry_model_river(method, metric, df):
    model_name = f"{method}_{metric}"

    with mlflow.start_run(run_name=model_name) as run:
        model = anomaly.LocalOutlierFactor(n_neighbors=10)

        print('learn__one')
        print(len(df.to_dict(orient='records')))
        i = 0
        for dict in df.to_dict(orient='records'):
            i = i + 1
            print(i)
            model.learn_one(dict)

        print('dump')
        with open('lof.pkl', 'wb') as f:
            pickle.dump(model, f)

        print('log')
        mlflow.pyfunc.log_model(
            python_model=CustomRiverModel(),
            artifact_path=model_name,
            registered_model_name=model_name,
            artifacts={'model_path': 'lof.pkl'}
        )

        # versions = client.get_latest_versions(name=model_name)
        # version = versions[-1].version
        # client.transition_model_version_stage(
        #     name=model_name,
        #     version=version,
        #     stage='Production',
        #     archive_existing_versions=True
        # )

        os.remove('lof.pkl')


def get_last_version_model_river(model_name):
    model_run_id = client.get_latest_versions(name=model_name, stages=["Production"])[0].run_id
    print(client.get_latest_versions(name=model_name, stages=["Production"])[0].version)
    model_uri = f"runs:/{model_run_id}/{model_name}"
    custom_model = mlflow.pyfunc.load_model(model_uri)
    model = custom_model.predict(None)

    return model


def get_last_version_model_keras(model_name):
    print(client.get_latest_versions(name=model_name, stages=["Production"])[0].version)
    model_run_id = client.get_latest_versions(name=model_name, stages=["Production"])[0].run_id
    model_uri = f"runs:/{model_run_id}/{model_name}"
    return mlflow.tensorflow.load_model(model_uri)


def update_model(model, model_name, model_type):
    with mlflow.start_run(run_name=model_name) as run:
        if model_type == 'keras':
            mlflow.tensorflow.log_model(
                model=model,
                artifact_path=model_name,
                keras_model_kwargs={"save_format": "h5"},
                registered_model_name=model_name
            )

        elif model_type == 'river':
            with open(f"{model_name}.pkl", 'wb') as f:
                pickle.dump(model, f)

            mlflow.pyfunc.log_model(
                python_model=CustomRiverModel(),
                artifact_path=model_name,
                registered_model_name=model_name,
                artifacts={'model_path': f"{model_name}.pkl"}
            )

            os.remove(f"{model_name}.pkl")

    versions = client.get_latest_versions(name=model_name, stages=["None"])
    version = versions[0].version
    print(f"new_version_for production_{version}")
    print(f"all_versions{versions}")
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage='Production',
        archive_existing_versions=True
    )


if __name__ == '__main__':
    mlflow.set_tracking_uri("http://localhost:5000/")
    mlflow.set_experiment("model_registry")
    # mlflow.create_experiment(
    #     name='model_registry',
    #     artifact_location='model_registry_artifacts'
    # )

    with mlflow.start_run(run_name='test_artifacts') as run:
        model = anomaly.OneClassSVM(nu=0.5)
        with open('ocsvm.pkl', 'wb') as f:
            pickle.dump(model, f)

        mlflow.pyfunc.log_model(
            python_model=CustomRiverModel(),
            artifact_path='ocsvm_model',
            artifacts={'pklfilepath': 'ocsvm.pkl'}
        )

        os.remove('ocsvm.pkl')
