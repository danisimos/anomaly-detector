var prometheus_url = ''
var use_anomaly_model = false;
var anomaly_model = '';
var div_id_cpu = 'graph_cpu';
var div_id_memory = 'graph_memory';
var timeframe = '1h'
var alert = false
var alertCount = 0;

function data_all_template() {
    return {
        x: [],
        y: [],
        type: 'scatter',
        mode: 'lines',
        name: 'data_all'
    }
}

function data_anomaly_template() {
    return {
        x: [],
        y: [],
        type: 'scatter',
        mode: 'markers',
        name: 'data_anomaly',
        line: {color: '#FF0000'}
    }
}

var data_all_cpu  = data_all_template()
var data_all_memory = data_all_template()
var data_anomaly_cpu  = data_anomaly_template()
var data_anomaly_memory = data_anomaly_template()

var data_cpu = [data_all_cpu, data_anomaly_cpu];
var data_memory = [data_all_memory, data_anomaly_memory];

var metrics = {'data_cpu': data_cpu, 'data_memory': data_memory}

$(document).ready(function() {
    $("#danger-alert").hide()
})

function setAlert() {
    alert = document.getElementById('alertCheckbox').checked;
}
function set_prometheus_url() {
    prometheus_url = document.getElementById('prometheusUrlId').value
    drawGraph()
    setSession()
}

function changeCurrentAnomalyModel() {
    use_anomaly_model = true;
    anomaly_model = document.querySelector('input[name="rate"]:checked').value;

    if(anomaly_model === 'Transformer' && !timeframe.endsWith('d')) {
        changeTimeframe('1d')
    }

    redrawGraphWithNewModel()
}

function changeTimeframe(timeframe_use) {
    if(timeframe_use != null) {
        timeframe = timeframe_use
    } else {
        timeframe = document.querySelector('input[name="timeframe"]:checked').value;
    }

    let url = "/metric?start=" + timeframe + "&end=now&prometheus_url=" + prometheus_url

    $.ajax({
            url:url,
            type: "POST",
            data: JSON.stringify({"time": [], "values": []}),
            contentType: "application/json; charset=utf-8",
            success: function (answer) {
                for(metric in metrics) {
                    metrics[metric][0]['x'] = answer[metric]['time_all']
                    metrics[metric][0]['y'] = answer[metric]['values_all']
                    metrics[metric][1]['x'] = answer[metric]['time_anomaly']
                    metrics[metric][1]['y'] = answer[metric]['values_anomaly']
                }

                Plotly.redraw(div_id_cpu, data_cpu);
                Plotly.redraw(div_id_memory, data_memory);

                if(use_anomaly_model) {
                    redrawGraphWithNewModel()
                }

            }
    })
}

function drawGraph() {
    url = "/metric?start=" + timeframe + "&end=now&prometheus_url=" + prometheus_url

    $.ajax({
            url:url,
            type: "POST",
            data: JSON.stringify({"time": [], "values": []}),
            contentType: "application/json; charset=utf-8",
            success: function (answer) {

                for(metric in metrics) {
                    metrics[metric][0]['x'] = answer[metric]['time_all']
                    metrics[metric][0]['y'] = answer[metric]['values_all']
                    metrics[metric][1]['x'] = answer[metric]['time_anomaly']
                    metrics[metric][1]['y'] = answer[metric]['values_anomaly']
                }

                Plotly.newPlot(div_id_cpu, data_cpu);
                Plotly.newPlot(div_id_memory, data_memory);

            }
        })




    const interval = setInterval(function() {

        url = "/metric?start=now&end=now&prometheus_url=" + prometheus_url
        send_info = {'data_cpu': {'time': [], 'values': []}, 'data_memory': {'time': [], 'values': []}};

        if(use_anomaly_model) {
            url = url + "&anomaly_model=" + anomaly_model
            send_info = {
                'data_cpu': {'time': data_cpu[0]['x'], 'values': data_cpu[0]['y']},
                'data_memory': {'time': data_memory[0]['x'], 'values': data_memory[0]['y']}
            }
        }

        if(anomaly_model !== 'Transformer' && anomaly_model !== 'LOF' && !timeframe.endsWith('d') && !timeframe.endsWith('8h') && !timeframe.endsWith('1h')) {
            $.ajax({
                url:url,
                type: "POST",
                data: JSON.stringify(send_info),
                contentType: "application/json; charset=utf-8",
                success: function (newData) {

                    //remove old interval last value
                    for(metric in metrics) {
                        x_to_removed = metrics[metric][0]['x'].shift();
                        y_to_removed = metrics[metric][0]['y'].shift();

                        if(x_to_removed === metrics[metric][1]['x'][0]){
                            metrics[metric][1]['x'].shift();
                            metrics[metric][1]['y'].shift();
                        }

                        // add new interval first value
                        metrics[metric][0]['x'].push(newData[metric]['time_all'][0]);
                        metrics[metric][0]['y'].push(newData[metric]['values_all'][0]);

                        if(use_anomaly_model && newData[metric]['time_anomaly'].length > 0) {
                            metrics[metric][1]['x'].push(newData[metric]['time_anomaly'][0]);
                            metrics[metric][1]['y'].push(newData[metric]['values_anomaly'][0]);
                            showAlert()
                        }
                    }

                    Plotly.redraw(div_id_cpu);
                    Plotly.redraw(div_id_memory);
                }
            })
        }

    }, 1000);
}

function redrawGraphWithNewModel() {
    document.querySelector('.preloader-wrapper-cpu').style.opacity = '1'
    document.querySelector('.preloader-wrapper-memory').style.opacity = '1'

    url = "/anomaly?anomaly_model=" + anomaly_model + "&prometheus_url=" + prometheus_url

    send_info_change_model = {
        'data_cpu': {'time': data_cpu[0]['x'], 'values': data_cpu[0]['y']},
        'data_memory': {'time': data_memory[0]['x'], 'values': data_memory[0]['y']}
    }

    $.ajax({
            url: url,
            type: "POST",
            data: JSON.stringify(send_info_change_model),
            contentType: "application/json; charset=utf-8",
            success: function (newData) {
                for(metric in metrics) {
                    metrics[metric][1]['x'] = newData[metric]['time_anomaly'];
                    metrics[metric][1]['y'] = newData[metric]['values_anomaly'];
                }

                Plotly.redraw(div_id_cpu);
                Plotly.redraw(div_id_memory);

                document.querySelector('.preloader-wrapper-cpu').style.opacity = '0'
                document.querySelector('.preloader-wrapper-memory').style.opacity = '0'
            }
    })
}

function setSession() {
    $.ajax({
            url: '/session?alert=' + alert + '&prometheus_url=' + prometheus_url,
            type: "POST",
            success: function (data) {
                console.log(data)
            }
        })
}

function showAlert() {
    alertCount++;

    if(alertCount === 3) {
        const audio = new Audio('/static/sound/alert.mp3');
        audio.play();

        $("#danger-alert").fadeTo(2000, 500).slideUp(500, function() {
            $("#success-alert").slideUp(500);
        });

        alertCount = 0;
    }
}