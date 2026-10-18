"""
ml_model.py — The AI brain of our log analyzer.
Uses Isolation Forest to detect unusual patterns in log data.
"""

from sklearn.ensemble import IsolationForest
import pandas as pd


def prepare_features(logs):
    data = []
    for log in logs:
        level_map = {"INFO": 1, "WARN": 2, "ERROR": 3}
        level_num = level_map.get(log['level'], 1)

        try:
            hour = int(log['timestamp'].split(' ')[1].split(':')[0])
        except:
            hour = 12

        msg_length = len(log['message'])

        data.append({
            'level_numeric': level_num,
            'hour': hour,
            'message_length': msg_length,
        })

    return pd.DataFrame(data)


def detect_anomalies(logs, contamination=0.1):
    if len(logs) < 5:
        return [], logs, None

    X = prepare_features(logs)

    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42
    )
    model.fit(X)

    # FIX 1: Calculate predictions and scores ONCE for all logs, not in a loop
    predictions = model.predict(X)
    scores = model.decision_function(X)

    anomalous = []
    normal = []

    for i, log in enumerate(logs):
        log['anomaly_score'] = float(scores[i])

        if predictions[i] == -1:
            log['is_anomaly'] = True
            anomalous.append(log)
        else:
            log['is_anomaly'] = False
            normal.append(log)

    # FIX 2: Sort anomalies worst-first. Most negative score = most anomalous
    anomalous.sort(key=lambda x: x['anomaly_score'])

    return anomalous, normal, model


def get_anomaly_summary(anomalous_logs):
    if not anomalous_logs:
        return {'total_anomalies': 0}

    summary = {
        'total_anomalies': len(anomalous_logs),
        'error_count': sum(1 for l in anomalous_logs if l['level'] == 'ERROR'),
        'warn_count': sum(1 for l in anomalous_logs if l['level'] == 'WARN'),
        'info_count': sum(1 for l in anomalous_logs if l['level'] == 'INFO'),
        'examples': anomalous_logs[:5]
    }

    return summary