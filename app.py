from flask import Flask, render_template, request, redirect, url_for
from parser import parse_file, parse_line
from db import save_logs, get_all_logs, get_log_counts, clear_all_logs
from ml_model import detect_anomalies, get_anomaly_summary

app = Flask(__name__)

@app.route('/clear')
def clear():
    """Deletes all logs from the database. Useful for testing."""
    deleted = clear_all_logs()
    return f"""
    <div style="font-family: Arial; padding: 40px;">
        <h2>Database cleared</h2>
        <p>Deleted {deleted} log entries.</p>
        <a href="/">Go to upload page</a>
    </div>
    """

@app.route('/')
def home():
    """Main upload page."""
    return render_template('index.html')


@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')  # We'll create this template soon

@app.route('/upload', methods=['POST'])
def upload():
    """Handles upload → parse → store → analyze with AI → show results."""
    
    uploaded_file = request.files['logfile']
    
    if not uploaded_file.filename:
        return redirect(url_for('home'))
    
    # Parse
    content = uploaded_file.read().decode('utf-8')
    raw_lines = content.splitlines()
    logs = parse_file(raw_lines)
    
    # Save to DB
    saved_count = save_logs(logs)
    
    # Run AI Anomaly Detection
    anomalous, normal, model = detect_anomalies(logs)
    summary = get_anomaly_summary(anomalous)
    
    # Get overall counts
    counts = get_log_counts()
    
    return render_template(
        'results.html',
        filename=uploaded_file.filename,
        logs=logs,
        total=len(logs),
        count_info=counts['INFO'],
        count_warn=counts['WARN'],
        count_error=counts['ERROR'],
        total_saved=saved_count,
        
        # NEW: AI Results
        anomalies=anomalous,
        anomaly_summary=summary,
        has_anomalies=len(anomalous) > 0
    )

@app.route('/dashboard')
def dashboard():
    """
    Shows ALL logs ever uploaded (persistent view from MongoDB).
    This is the "memory" of your application.
    """
    all_logs = get_all_logs()
    counts = get_log_counts()
    
    return render_template(
        'dashboard.html',
        logs=all_logs,
        total=len(all_logs),
        count_info=counts['INFO'],
        count_warn=counts['WARN'],
        count_error=counts['ERROR']
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)