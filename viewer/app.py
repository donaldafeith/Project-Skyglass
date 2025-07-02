# viewer/app.py

import sqlite3
from flask import Flask, render_template
from pathlib import Path

app = Flask(__name__)
# Correctly locate the database relative to this file's location
DB_FILE = Path(__file__).parent.parent / "registry/skyglass_log.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    if not DB_FILE.exists():
        return None
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Renders the main dashboard page, showing the latest logged data entries."""
    conn = get_db_connection()
    if not conn:
        return "<h1>Skyglass Viewer</h1><p>Database not found. Please run 'python skyglass.py setup' and 'python skyglass.py fetch' first.</p>"
        
    log_entries = conn.execute('SELECT * FROM data_log ORDER BY timestamp DESC LIMIT 100').fetchall()
    conn.close()
    return render_template('index.html', entries=log_entries)

def run_viewer():
    """Function to run the Flask app."""
    app.run(host='127.0.0.1', port=5656, debug=False)
