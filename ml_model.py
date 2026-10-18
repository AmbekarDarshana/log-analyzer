"""
ml_model.py — The AI brain of our log analyzer.
Uses Isolation Forest to detect unusual patterns in log data.
"""

from sklearn.ensemble import IsolationForest
import pandas as pd


def prepare_features(logs):
    """
    Converts raw log dictionaries into numbers the ML model can understand.
    Machines only understand numbers, not words like 'ERROR' or 'INFO'.
    
    Returns: A DataFrame with numeric features.
    """
    
    data = []
    
    for log in logs:
        # Convert log level to a number
        level_map = {"INFO": 1, "WARN": 2, "ERROR": 3}
        level_num = level_map.get(log['level'], 1)
        
        # Extract hour from timestamp (for time-based patterns)
        # Example: "2026-10-17 10:02:03" -> hour = 10
        try:
            hour = int(log['timestamp'].split(' ')[1].split(':')[0])
        except:
            hour = 12  # default if parsing fails
        
        # Count length of message (long messages might be error stack traces)
        msg_length = len(log['message'])
        
        data.append({
            'level_numeric': level_num,
            'hour': hour,
            'message_length': msg_length,
            # We'll add more features later (response time, IP count, etc.)
        })
    
    return pd.DataFrame(data)


def detect_anomalies(logs, contamination=0.1):
    """
    Runs Isolation Forest on the logs and flags anomalies.
    
    Parameters:
        logs: list of parsed log dictionaries
        contamination: how much of the data we expect to be anomalous
                       0.1 = assume ~10% are unusual
    
    Returns: 
        Tuple of (anomalous_logs, normal_logs, model)
    """
    
    if len(logs) < 5:
        # Need at least some data to detect patterns
        return [], logs, None
    
    # Step 1: Convert logs to numeric features
    X = prepare_features(logs)
    
    # Step 2: Create and train the model
    # n_estimators=100 = use 100 decision trees (more = better but slower)
    # contamination=0.1 = expect 10% anomalies
    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42
    )
    
    # Fit the model (let it learn the patterns)
    model.fit(X)
    
    # Step 3: Predict which ones are anomalies
    # prediction = 1 means NORMAL
    # prediction = -1 means ANOMALY
    predictions = model.predict(X)
    
    # Step 4: Split logs into two groups
    anomalous = []
    normal = []
    
    for i, log in enumerate(logs):
        if predictions[i] == -1:
            log['is_anomaly'] = True
            log['anomaly_score'] = float(model.decision_function([X.iloc[i]])[0])
            anomalous.append(log)
        else:
            log['is_anomaly'] = False
            normal.append(log)
    
    return anomalous, normal, model


def get_anomaly_summary(anomalous_logs):
    """
    Creates a human-readable summary of detected anomalies.
    """
    
    if not anomalous_logs:
        return {
            'total_anomalies': 0,
            'error_spike': False,
            'unusual_hours': [],
            'long_messages': []
        }
    
    summary = {
        'total_anomalies': len(anomalous_logs),
        'error_count': sum(1 for l in anomalous_logs if l['level'] == 'ERROR'),
        'warn_count': sum(1 for l in anomalous_logs if l['level'] == 'WARN'),
        'info_count': sum(1 for l in anomalous_logs if l['level'] == 'INFO'),
        'examples': anomalous_logs[:5]  # Show first 5 as examples
    }
    
    return summary