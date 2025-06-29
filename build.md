build_instructions.md (v4.0 - Full Specification)
Skyglass Operational Console - LOCAL DESKTOP Automated Build Script
Target OS: Ubuntu 22.04 LTS (for automated build environment)
Final App: Cross-platform (Windows, macOS, Linux) via Electron
This script builds a self-contained, offline-first desktop application.
It includes functional data collectors and advanced features for integrity,
testing, backup, and extensibility. It does not set up a public web server.
#!/bin/bash
set -e

--- Variables ---
PROJECT_DIR="skyglass-operational-console"

--- Helper Functions ---
function print_header() {
echo ""
echo "========================================================================"
echo "  $1"
echo "========================================================================"
}

--- STAGE 1: SYSTEM SETUP ---
print_header "STAGE 1: Installing Build Dependencies (Python, Node.js)"
sudo apt-get update -y
sudo apt-get install -y python3.10-venv python3-pip python3-dev build-essential git curl
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

--- STAGE 2: PROJECT STRUCTURE AND BACKEND SETUP ---
print_header "STAGE 2: Creating Project Structure & Python Backend"
mkdir -p $PROJECT_DIR && cd $PROJECT_DIR
mkdir -p backend/app/api backend/app/models backend/app/collectors backend/app/services backend/tests backend/cli backend/app/plugins

--- Create Backend Files ---
Create backend/.env
cat << 'EOF' > backend/.env

Skyglass Backend Configuration
FLASK_APP=main.py
FLASK_ENV=development

--- API KEYS (Get from provider dashboards - see README) ---
FIRMS_API_KEY=""
RAINVIEWER_API_KEY=""
OPENAQ_API_KEY=""
EOF

Create backend/requirements.txt
cat << 'EOF' > backend/requirements.txt
Flask==2.2.2
Flask-SQLAlchemy==3.0.3
Flask-Migrate==4.0.4
python-dotenv==0.21.1
requests==2.28.2
APScheduler==3.10.1
pandas==1.5.3
Flask-Cors==3.0.10
EOF

Create backend/config.py
cat << 'EOF' > backend/config.py
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(file))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 

'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SCHEDULER_API_ENABLED = True
FIRMS_API_KEY = os.environ.get('FIRMS_API_KEY')
RAINVIEWER_API_KEY = os.environ.get('RAINVIEWER_API_KEY')
OPENAQ_API_KEY = os.environ.get('OPENAQ_API_KEY')
EOF

Create backend/main.py
cat << 'EOF' > backend/main.py
from app import create_app, db
from app.models import DataLog

app = create_app()

@app.shell_context_processor
def make_shell_context():
return {'db': db, 'DataLog': DataLog}
EOF

Create backend/app/init.py
cat << 'EOF' > backend/app/init.py
import os
import importlib
from flask import Flask
from flask_cors import CORS
from config import Config
from .extensions import db, migrate
from .services.scheduler import start_scheduler

def load_plugins(app):
plugins_dir = os.path.join(os.path.dirname(file), 'plugins')
if not os.path.exists(plugins_dir): return
for filename in os.listdir(plugins_dir):
if filename.endswith('.py') and not filename.startswith('__'):
module_name = f"app.plugins.{filename[:-3]}"
try:
plugin = importlib.import_module(module_name)
if hasattr(plugin, 'init_app'):
plugin.init_app(app)
print(f"Loaded plugin: {module_name}")
except Exception as e:
print(f"Failed to load plugin {module_name}: {e}")

def create_app(config_class=Config):
app = Flask(name)
app.config.from_object(config_class)
CORS(app)

db.init_app(app)
migrate.init_app(app, db)

with app.app_context():
    db.create_all()

from .api.data_routes import data_bp
app.register_blueprint(data_bp, url_prefix='/api')

load_plugins(app)

if app.config['SCHEDULER_API_ENABLED']:
    start_scheduler(app)

return app

EOF

Create backend/app/extensions.py
cat << 'EOF' > backend/app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
db = SQLAlchemy()
migrate = Migrate()
EOF

Create backend/app/models.py
cat << 'EOF' > backend/app/models.py
from app.extensions import db
import datetime

class DataLog(db.Model):
id = db.Column(db.Integer, primary_key=True)
source = db.Column(db.String(50), nullable=False, index=True)
timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)
data = db.Column(db.JSON, nullable=False)
success = db.Column(db.Boolean, default=True)
error_message = db.Column(db.String(255), nullable=True)
data_hash = db.Column(db.String(64), index=True, nullable=True)
EOF

--- Create Data Collectors ---
cat << 'EOF' > backend/app/collectors/firms_collector.py
import requests, pandas as pd
from io import StringIO
from config import Config

def fetch_data():
if not Config.FIRMS_API_KEY: return {"error": "FIRMS_API_KEY not configured"}
url = f"https://firms.modaps.eosdis.nasa.gov/api/v1/nrt/viirs-snpp-j1/csv/{Config.FIRMS_API_KEY}/world/1"
try:
response = requests.get(url, timeout=30)
response.raise_for_status()
if not response.text: return {"type": "FeatureCollection", "features": []}
df = pd.read_csv(StringIO(response.text))
features = [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [row['longitude'], row['latitude']]}, "properties": { "brightness": row['bright_ti4'], "confidence": row['confidence'], "frp": row['frp'], "acq_time": row['acq_time']}} for _, row in df.iterrows()]
return {"type": "FeatureCollection", "features": features}
except Exception as e: return {"error": f"FIRMS Collector Error: {str(e)}"}
EOF

cat << 'EOF' > backend/app/collectors/usgs_seismic_collector.py
import requests
def fetch_data():
url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
try:
r = requests.get(url, timeout=15); r.raise_for_status(); return r.json()
except Exception as e: return {"error": f"USGS Seismic Collector Error: {str(e)}"}
EOF

--- Create Services ---
cat << 'EOF' > backend/app/services/data_processor.py
from app.extensions import db
from app.models import DataLog
import json, hashlib

def hash_data(data):
return hashlib.sha256(json.dumps(data, sort_keys=True).encode('utf-8')).hexdigest()

def process_and_store(app, source, raw_data):
with app.app_context():
if isinstance(raw_data, dict) and "error" in raw_data:
log_entry = DataLog(source=source, success=False, error_message=str(raw_data["error"]), data={})
print(f"DATA PROCESSOR: Logged FAILURE for {source}: {raw_data['error']}")
else:
data_hash = hash_data(raw_data)
log_entry = DataLog(source=source, success=True, data=raw_data, data_hash=data_hash)
print(f"DATA PROCESSOR: Logged SUCCESS for {source} with hash {data_hash[:10]}...")
db.session.add(log_entry)
db.session.commit()
EOF

cat << 'EOF' > backend/app/services/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from app.collectors import firms_collector, usgs_seismic_collector
from app.services.data_processor import process_and_store

def run_collection_job(app, source, collector_module):
print(f"SCHEDULER: Fetching data for {source}...")
try:
raw_data = collector_module.fetch_data()
process_and_store(app, source, raw_data)
except Exception as e:
process_and_store(app, source, {"error": f"Unhandled exception: {e}"})

def start_scheduler(app):
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(run_collection_job, 'interval', minutes=20, args=[app, 'wildfires_firms', firms_collector], id='firms_job')
scheduler.add_job(run_collection_job, 'interval', minutes=5, args=[app, 'earthquakes_usgs', usgs_seismic_collector], id='usgs_job')
if not scheduler.running:
scheduler.start()
print("Background data collection scheduler started.")
EOF

--- Create API Routes ---
cat << 'EOF' > backend/app/api/data_routes.py
from flask import Blueprint, jsonify
from app.models import DataLog
from sqlalchemy import desc

data_bp = Blueprint('data_bp', name)

@data_bp.route('/status', methods=['GET'])
def status():
return jsonify(message="Skyglass Backend Service is Active")

@data_bp.route('/latest/string:source', methods=['GET'])
def get_latest_data(source):
entry = DataLog.query.filter_by(source=source, success=True).order_by(desc(DataLog.timestamp)).first()
if entry: return jsonify(entry.data)
last_error = DataLog.query.filter_by(source=source, success=False).order_by(desc(DataLog.timestamp)).first()
if last_error: return jsonify({"error": f"Last attempt failed: {last_error.error_message}"}), 500
return jsonify({"error": "No data found. The scheduler may not have run yet."}), 404
EOF

--- Create Test Suite and Backup Scripts ---
cat << 'EOF' > backend/tests/test_data_integrity.py
import unittest
from app import create_app, db
from app.models import DataLog

class DataTests(unittest.TestCase):
def setUp(self):
self.app = create_app()
self.app.config['TESTING'] = True
self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
self.app_context = self.app.app_context()
self.app_context.push()
db.create_all()

def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

def test_log_entry_creation(self):
    log = DataLog(source='test', data={'key': 'value'}, data_hash='abc')
    db.session.add(log)
    db.session.commit()
    self.assertEqual(DataLog.query.count(), 1)
    self.assertEqual(DataLog.query.first().source, 'test')

if name == 'main':
unittest.main()
EOF

cat << 'EOF' > backend/cli/export_backup.py
import os, shutil
from datetime import datetime

def export_backup():
project_root = os.path.abspath(os.path.join(os.path.dirname(file), '..'))
db_path = os.path.join(project_root, 'app.db')
timestamp = datetime.now().strftime('%Y%m%d_%H%M')
backup_root = os.path.join(os.path.expanduser("~"), f'skyglass_backup_{timestamp}')
os.makedirs(backup_root, exist_ok=True)

if os.path.exists(db_path):
    shutil.copy(db_path, os.path.join(backup_root, 'app.db'))
    print(f"Database backed up to {backup_root}")
else:
    print(f"Database file not found at {db_path}, skipping backup.")

if name == 'main':
export_backup()
EOF

--- STAGE 3: BACKEND ENVIRONMENT AND DATABASE INITIALIZATION ---
print_header "STAGE 3: Initializing Python Backend Environment"
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
flask db init || echo "Migrations folder already exists."
flask db migrate -m "Initial schema"
flask db upgrade
deactivate
cd ..

--- STAGE 4: FRONTEND (ELECTRON + REACT) SETUP ---
print_header "STAGE 4: Setting Up Electron + React Frontend"

cat << 'EOF' > package.json
{
"name": "skyglass-operational-console",
"version": "4.0.0",
"description": "A standalone, multi-source environmental intelligence platform.",
"main": "main.js",
"scripts": {
"start": "concurrently -k "npm:start-backend" "npm:start-frontend"",
"start-backend": "cd backend && . venv/bin/activate && flask run --port=5555",
"start-frontend": "wait-on http://127.0.0.1:5555 && electron .",
"build-react": "cd frontend && npm run build",
"package": "npm run build-react && electron-builder",
"test-backend": "cd backend && . venv/bin/activate && python -m unittest discover -s tests",
"backup": "cd backend && . venv/bin/activate && python cli/export_backup.py"
},
"devDependencies": {
"concurrently": "^7.6.0",
"electron": "^22.0.0",
"electron-builder": "^23.6.0",
"wait-on": "^7.0.1"
},
"build": {
"appId": "com.skyglass.console",
"files": [ "main.js", "frontend/build//*", "node_modules//*" ],
"extraResources": [ { "from": "backend", "to": "backend" } ]
}
}
EOF

cat << 'EOF' > main.js
const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

function createMainWindow() {
mainWindow = new BrowserWindow({ width: 1800, height: 1200, webPreferences: { nodeIntegration: true, contextIsolation: false } });
mainWindow.loadFile(path.join(__dirname, './frontend/build/index.html'));
}

function startPythonBackend() {
const backendPath = app.isPackaged ? path.join(process.resourcesPath, 'backend') : path.join(__dirname, 'backend');
const script = (process.platform === 'win32') ? 'flask.exe' : 'flask';
const venvPath = (process.platform === 'win32') ? 'Scripts' : 'bin';
const scriptPath = path.join(backendPath, 'venv', venvPath, script);

pythonProcess = spawn(scriptPath, ['run', '--port=5555'], { cwd: backendPath });
pythonProcess.stdout.on('data', (data) => console.log(`Python Backend: ${data}`));
pythonProcess.stderr.on('data', (data) => console.error(`Python Backend Error: ${data}`));

}

app.whenReady().then(() => {
if (app.isPackaged) startPythonBackend();
createMainWindow();
});

app.on('window-all-closed', () => process.platform !== 'darwin' && app.quit());
app.on('will-quit', () => pythonProcess && pythonProcess.kill());
EOF

--- Create React Frontend ---
print_header "STAGE 5: Creating React Frontend"
mkdir -p frontend
cd frontend
npx create-react-app .

cat << 'EOF' > src/App.js
import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
const [status, setStatus] = useState('Connecting...');
const [dataLayers, setDataLayers] = useState({ earthquakes_usgs: null, wildfires_firms: null });

useEffect(() => {
const fetchStatus = () => {
fetch('http://127.0.0.1:5555/api/status')
.then(res => res.ok ? res.json() : Promise.reject(res))
.then(data => setStatus(data.message))
.catch(() => setStatus('Connection FAILED. Is the backend running?'));
};

const fetchDataForSource = (source) => {
  fetch(`http://127.0.0.1:5555/api/latest/${source}`)
    .then(res => res.ok ? res.json() : res.json().then(err => Promise.reject(err)))
    .then(data => setDataLayers(prev => ({...prev, [source]: data})))
    .catch(err => setDataLayers(prev => ({...prev, [source]: { error: err.error || "Fetch failed" }})));
};

fetchStatus();
const sources = ['earthquakes_usgs', 'wildfires_firms'];
sources.forEach(fetchDataForSource);
const interval = setInterval(() => sources.forEach(fetchDataForSource), 300000); // 5 min refresh
return () => clearInterval(interval);

}, []);

const renderFeatureCount = (data) => {
if (!data) return Fetching...;
if (data.error) return ERROR;
if (data.features) return {data.features.length} active;
return No data;
};

return (


Skyglass Console
Backend Status: {status}

Real-Time Layers
USGS Earthquakes (2.5+){renderFeatureCount(dataLayers.earthquakes_usgs)}
FIRMS Wildfires{renderFeatureCount(dataLayers.wildfires_firms)}



Operational Map

This area will contain the main interactive map (e.g., Leaflet.js).
Live data is being fetched from the local backend and displayed in the sidebar.



);
}
export default App;
EOF

cat << 'EOF' > src/App.css
:root {
--bg-dark: #1a1d21; --bg-medium: #2c313a; --bg-light: #383e4a;
--text-primary: #e6edf3; --text-secondary: #7d8590;
--accent-blue: #58a6ff; --accent-red: #f85149; --accent-yellow: #e3b341; --accent-green: #3fb950;
}
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background-color: var(--bg-dark); color: var(--text-primary); }
.container { display: flex; height: 100vh; }
.sidebar { width: 350px; background-color: var(--bg-medium); padding: 20px; display: flex; flex-direction: column; border-right: 1px solid var(--bg-light); }
.sidebar h1 { font-size: 1.5rem; margin: 0 0 20px 0; }
.status-box { border: 1px solid var(--bg-light); padding: 10px; margin-bottom: 20px; border-radius: 6px; font-size: 0.9rem; background-color: var(--bg-dark); }
.layer-nav h2 { font-size: 1rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid var(--bg-light); padding-bottom: 10px; margin-bottom: 10px; }
.layer-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 5px; font-size: 0.95rem; border-radius: 4px; }
.layer-item:nth-child(odd) { background-color: rgba(0,0,0,0.1); }
.data-count { font-weight: bold; }
.data-count.success { color: var(--accent-green); }
.data-count.loading { color: var(--accent-blue); }
.data-count.error { color: var(--accent-red); cursor: help; }
.data-count.unknown { color: var(--text-secondary); }
.main-content { flex-grow: 1; padding: 20px; }
.map-placeholder { width: 100%; height: 80vh; display: flex; flex-direction: column; align-items: center; justify-content: center; border: 2px dashed var(--bg-light); border-radius: 8px; background-color: var(--bg-dark); color: var(--text-secondary); }
EOF
cd ..

--- STAGE 6: FINAL INSTALLATIONS ---
print_header "STAGE 6: Installing Root & Frontend Node.js Dependencies"
npm install
cd frontend
npm install
cd ..

print_header "BUILD COMPLETE"
echo ""
echo "The Skyglass Operational Console project has been created in the '$PROJECT_DIR' directory."
echo "To run in development mode:"
echo "1. cd $PROJECT_DIR"
echo "2. Edit backend/.env to add your API keys (see README)."
echo "3. npm start"
echo ""
echo "To create a distributable package:"
echo "1. cd $PROJECT_DIR"
echo "2. npm run package"
echo "The executable will be in the 'dist' directory."
echo ""
echo "Additional commands available:"
echo " - npm run test-backend"
echo " - npm run backup"
