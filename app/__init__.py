import logging
import app.utils as utils


import pandas as pd
from flask import Flask, jsonify, request, render_template, session

from app.models import find_anomalies_from_df
from app.models.iqr import get_column_outliers
from app.utils import get_prometheus_metrics, get_df_from_prometheus_metrics, get_df_from_ajax_json, \
    get_anomaly_time_series_from_df, get_time_series_from_df

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)
# def sensor():
#     logging.debug("Scheduler is alive!")
#
#
# schedule = BackgroundScheduler(daemon=True)
# schedule.add_job(sensor, 'interval', minutes=1)
# schedule.start()

app = Flask(__name__, template_folder='../templates', static_folder="../static")




@app.route('/health')
def health():
    resp = jsonify(health="healthy")
    resp.status_code = 200

    return resp


@app.route('/')
def index():



    return render_template('index.jinja', alert=session.get('alert', False), prometheus_url=session.get('prometheus_url', ''))

@app.route('/methods')
def methods():
    return render_template('methods.jinja')

@app.route('/alerts')
def alerts():

    return render_template('alerts.jinja', alert=session.get('alert', False))



@app.route('/metric', methods=['POST'])
def get_metrics():
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    anomaly_model = request.args.get('anomaly_model')
    prometheus_url = request.args.get('prometheus_url')
    ajax_request = request.json

    time_cpu, values_cpu, time_anomaly_cpu, values_anomaly_cpu = (
        utils.get_metrics(start_time, end_time, prometheus_url, anomaly_model, request.json.get('data_cpu'), 'cpu')
    )

    time_memory, values_memory, time_anomaly_memory, values_anomaly_memory = (
        utils.get_metrics(start_time, end_time, prometheus_url, anomaly_model, request.json.get('data_memory'), 'memory')
    )

    response = {
        'data_cpu': {
            'time_all': time_cpu,
            'values_all': values_cpu,
            'time_anomaly': time_anomaly_cpu,
            'values_anomaly': values_anomaly_cpu
        },
        'data_memory': {
            'time_all': time_memory,
            'values_all': values_memory,
            'time_anomaly': time_anomaly_memory,
            'values_anomaly': values_anomaly_memory
        }
    }


    return jsonify(response)


@app.route('/anomaly', methods=['POST'])
def get_anomalies():
    anomaly_model = request.args.get('anomaly_model')

    df_cpu = get_df_from_ajax_json(request.json.get('data_cpu'))
    df_cpu = find_anomalies_from_df(df_cpu, anomaly_model, 'cpu')
    time_all_cpu, values_all_cpu, time_anomaly_cpu, values_anomaly_cpu = get_anomaly_time_series_from_df(df_cpu)

    df_memory = get_df_from_ajax_json(request.json.get('data_memory'))
    df_memory = find_anomalies_from_df(df_memory, anomaly_model, 'memory')
    time_all_memory, values_all_memory, time_anomaly_memory, values_anomaly_memory = get_anomaly_time_series_from_df(df_memory)

    return jsonify({
        'data_cpu': {
            'time_all': time_all_cpu,
            'values_all': values_all_cpu,
            'time_anomaly': time_anomaly_cpu,
            'values_anomaly': values_anomaly_cpu
        },
        'data_memory': {
            'time_all': time_all_memory,
            'values_all': values_all_memory,
            'time_anomaly': time_anomaly_memory,
            'values_anomaly': values_anomaly_memory
        }
    })


@app.route('/session', methods=['POST'])
def update_session():
    session['alert'] = request.args.get('alert')
    session['prometheus_url'] = request.args.get('prometheus_url')




    return jsonify({'status': '200'})
