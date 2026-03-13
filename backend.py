from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
# In-memory storage (replace with a database like SQLite for real persistence)
tasks = []

@app.route('/')
def task_page():
    return render_template('index.html', tasks=tasks)

# API to add a task
@app.route('/api/add', methods=['POST'])
def add_task():
    task = request.json.get('task')
    if task and task.strip():
        tasks.append(task.strip())
        return jsonify({"success": True, "tasks": tasks})
    return jsonify({"success": False, "error": "Empty task!"})

# API to delete a task
@app.route('/api/delete', methods=['POST'])
def delete_task():
    task = request.json.get('task')
    if task in tasks:
        tasks.remove(task)
        return jsonify({"success": True, "tasks": tasks})
    return jsonify({"success": False, "error": "Task not found!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=443)  # Use port 5000 (443 needs SSL)