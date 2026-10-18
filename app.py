from flask import Flask, render_template, request, redirect, url_for
from parser import parse_file, parse_line
from db import save_logs, get_all_logs, get_log_counts

app = Flask(__name__)


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
    """
    Handles log file upload.
    Flow: receive file → parse lines → save to DB → show results.
    """
    # 1. Get the uploaded file
    uploaded_file = request.files['logfile']
    
    if not uploaded_file.filename:
        return redirect(url_for('home'))
    
    # 2. Read and parse
    content = uploaded_file.read().decode('utf-8')
    raw_lines = content.splitlines()
    logs = parse_file(raw_lines)
    
    # 3. Save to MongoDB
    saved_count = save_logs(logs)
    
    # 4. Get updated counts from DB
    counts = get_log_counts()
    
    # 5. Render the same results template, now showing DB-backed data
    return render_template(
        'results.html',
        filename=uploaded_file.filename,
        logs=logs,
        total=len(logs),
        count_info=counts['INFO'],
        count_warn=counts['WARN'],
        count_error=counts['ERROR'],
        total_saved=saved_count
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