from flask import Flask, render_template, request
from parser import parse_file

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return "This is a log analyzer project. I am learning DevOps!"


@app.route('/upload', methods=['POST'])
def upload():
    # 1. Get the file and read it
    uploaded_file = request.files['logfile']
    content = uploaded_file.read().decode('utf-8')
    raw_lines = content.splitlines()

    # 2. Parse every line
    logs = parse_file(raw_lines)

    # 3. Count each level
    count_info = 0
    count_warn = 0
    count_error = 0

    for log in logs:
        if log['level'] == 'INFO':
            count_info += 1
        elif log['level'] == 'WARN':
            count_warn += 1
        elif log['level'] == 'ERROR':
            count_error += 1

    # 4. Render the results page, handing it our data
    return render_template(
        'results.html',
        filename=uploaded_file.filename,
        logs=logs,
        total=len(logs),
        count_info=count_info,
        count_warn=count_warn,
        count_error=count_error
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)