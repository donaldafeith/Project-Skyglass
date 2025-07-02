Project Skyglass: A Build Document for a Citizen-Led Weather Intelligence System
1. Project Philosophy & Mandate
In an environment where critical, publicly funded weather and earth observation data streams can be abruptly terminated, creating an information vacuum, an independent, citizen-operated system for monitoring our planet is no longer a hobbyist pursuit—it is a necessity. Project Skyglass is conceived as a direct response to this challenge.

Core Mandates:

Data Sovereignty: To empower individuals and communities with direct, unmediated, and uncensored access to raw satellite imagery and atmospheric data.

Operational Resilience: To construct a decentralized system that is not dependent on a single point of failure or a central authority that can be compromised or shut down.

Immutable Truth: To establish a verifiable, cryptographically-secured ledger of weather events, creating a tamper-proof historical record that can be audited and trusted.

Independent Foresight: To provide tools that enable any user to analyze, interpret, and forecast weather patterns, moving beyond passive consumption of official narratives to active, critical observation.

Project Skyglass is not another weather application. It is a distributed, open-source instrument of observational truth.

2. System Architecture
The system is designed with modularity and local-first operation as its core principles. Each component is self-contained but works in concert with the others.

The Collector (collector/): A series of Python modules responsible for connecting to and retrieving data from a curated list of non-governmental, international, and commercial satellite constellations.

The Registry (registry/): An immutable logging system. It uses cryptographic hashing (SHA256) to fingerprint every piece of collected data, which is then recorded in a local SQLite database, creating a verifiable chain of evidence.

The Viewer (viewer/): A local web dashboard served by a lightweight Flask application. It provides an interface to visualize the collected imagery, compare data layers over time, and inspect the integrity of the data log.

The Conductor (skyglass.py): The master Command-Line Interface (CLI) built with Python's click library. It acts as the central control panel for all system operations: setup, fetch, and view.

3. Directory and File Structure
The project will be organized with the following directory structure to ensure modularity and clarity.

/project_skyglass/
|
|├── build.md                # This document
|├── requirements.txt        # A list of all necessary Python libraries
|├── .env.example            # Example for environment variable configuration
|├── skyglass.py             # The main CLI script for orchestration
|
|├── collector/
|│   ├── __init__.py
|│   └── sentinel_api.py     # Module for fetching data from ESA's Sentinel satellites
|
|├── registry/
|│   ├── __init__.py
|│   ├── logger.py           # Module for hashing files and logging to the database
|│   └── skyglass_log.db     # The SQLite database file for the immutable log
|
|├── viewer/
|│   ├── app.py              # The Flask web application to serve the viewer
|│   ├── templates/
|│   │   └── index.html      # HTML template for the main dashboard page
|│   └── static/
|│       ├── css/
|│       │   └── style.css   # CSS for styling the dashboard
|│       └── js/
|│           └── app.js      # Placeholder for future JavaScript interactivity
|
└── data/
    └── satellite/
        └── sentinel-1/     # Directory where Sentinel-1 data will be stored

4. Code Implementation and Snippets
Below are the complete code snippets required to build each component of the system.

4.1. requirements.txt
This file defines the Python dependencies required for the project.

Plaintext

# Core application and CLI framework
click
python-dotenv

# For connecting to satellite data APIs and handling geospatial data
sentinelhub
rasterio
pyproj
shapely

# For the local web viewer
Flask

# For the database registry
SQLAlchemy

4.2. .env.example
This file serves as a template for users to configure their API credentials. Users should rename this to .env and fill in their credentials.

# Sentinel Hub Credentials from Copernicus
# Create a free account at https://dataspace.copernicus.eu/ to get these
SH_CLIENT_ID="Your_Sentinel_Hub_Client_ID_Here"
SH_CLIENT_SECRET="Your_Sentinel_Hub_Client_Secret_Here"

4.3. Collector Module: collector/sentinel_api.py
This module contains the logic for fetching radar imagery from the Sentinel-1 satellite.

Python

# collector/sentinel_api.py

import os
import datetime
from pathlib import Path
from sentinelhub import (
    SHConfig,
    SentinelHubRequest,
    DataCollection,
    MimeType,
    bbox_to_dimensions,
    BBox,
    CRS,
)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration from Environment Variables ---
SH_CLIENT_ID = os.environ.get("SH_CLIENT_ID")
SH_CLIENT_SECRET = os.environ.get("SH_CLIENT_SECRET")

config = SHConfig()

if not SH_CLIENT_ID or not SH_CLIENT_SECRET:
    print("WARNING: Sentinel Hub credentials (SH_CLIENT_ID, SH_CLIENT_SECRET) not found in .env file.")
    print("Please create a free account at https://dataspace.copernicus.eu/, create a .env file, and set your credentials.")
else:
    config.sh_client_id = SH_CLIENT_ID
    config.sh_client_secret = SH_CLIENT_SECRET
    config.save()

# --- Evalscript for Sentinel-1 Synthetic Aperture Radar (SAR) ---
# This script processes the raw radar data into a visual format.
evalscript_s1_sar = """
//VERSION=3
function setup() {
  return {
    input: ["VV", "VH"],
    output: { bands: 3 }
  };
}

function evaluatePixel(sample) {
  return [2.5 * sample.VV, 2.5 * sample.VH, 2.5 * (sample.VV - sample.VH)];
}
"""

def fetch_sentinel1_data(bbox_coords, start_date, end_date, output_path, resolution=500):
    """
    Fetches Sentinel-1 SAR data for a given bounding box and time range.

    Args:
        bbox_coords (list): A list of [min_lon, min_lat, max_lon, max_lat].
        start_date (datetime.date): The start date for the data query.
        end_date (datetime.date): The end date for the data query.
        output_path (Path): The pathlib.Path object for the output directory.
        resolution (int): The image resolution in meters.

    Returns:
        str: The file path of the saved image, or None if failed.
    """
    if not config.sh_client_id:
        print("Skipping Sentinel-1 download due to missing credentials.")
        return None

    try:
        bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)
        size = bbox_to_dimensions(bbox, resolution=resolution)
        time_interval = (f"{start_date.isoformat()}T00:00:00Z", f"{end_date.isoformat()}T23:59:59Z")

        print(f"Requesting Sentinel-1 data for bounding box {bbox_coords} of size {size} for interval {time_interval}")

        request = SentinelHubRequest(
            evalscript=evalscript_s1_sar,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL1_IW,
                    time_interval=time_interval,
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox,
            size=size,
            config=config,
        )

        image_data = request.get_data()[0]

        output_path.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"S1_{timestamp}.tiff"
        file_path = output_path / filename

        with open(file_path, "wb") as f:
            f.write(image_data)
            
        print(f"Successfully saved Sentinel-1 image to: {file_path}")
        return str(file_path)

    except Exception as e:
        print(f"An error occurred while fetching Sentinel-1 data: {e}")
        return None

4.4. Registry Module: registry/logger.py
This module manages the creation of the database and the logging of file hashes.

Python

# registry/logger.py

import sqlite3
import hashlib
import datetime
from pathlib import Path

DB_FILE = Path(__file__).parent / "skyglass_log.db"

def setup_database():
    """Initializes the database and creates the data_log table if it doesn't exist."""
    DB_FILE.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        file_path TEXT NOT NULL UNIQUE,
        sha256_hash TEXT NOT NULL,
        data_source TEXT NOT NULL,
        metadata TEXT
    );
    """)
    conn.commit()
    conn.close()
    print("Database setup is complete.")

def calculate_sha256(file_path):
    """Calculates the SHA256 hash of a file to ensure its integrity."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256.update(byte_block)
        return sha256.hexdigest()
    except FileNotFoundError:
        print(f"Error: Could not find file at {file_path} to hash.")
        return None

def log_data_entry(file_path, source, metadata="{}"):
    """
    Hashes a file and records its information in the SQLite database.

    Args:
        file_path (str): The path to the file to be logged.
        source (str): The name of the data source (e.g., 'Sentinel-1').
        metadata (str): A JSON string for any additional metadata.
    
    Returns:
        bool: True if logging was successful, False otherwise.
    """
    if not file_path:
        print("Logging failed: The provided file path is invalid.")
        return False
        
    file_hash = calculate_sha256(file_path)
    if not file_hash:
        return False

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO data_log (timestamp, file_path, sha256_hash, data_source, metadata) VALUES (?, ?, ?, ?, ?)",
            (datetime.datetime.now(datetime.timezone.utc).isoformat(), str(file_path), file_hash, source, metadata)
        )
        conn.commit()
        print(f"Successfully logged entry for: {file_path}")
        return True
    except sqlite3.IntegrityError:
        print(f"Record for {file_path} already exists in the log. Skipping.")
        return False
    except Exception as e:
        print(f"A database error occurred during logging: {e}")
        return False
    finally:
        conn.close()

4.5. Viewer Application: viewer/app.py
This Flask application serves the front-end dashboard.

Python

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

4.6. Viewer Frontend: viewer/templates/index.html
The HTML for the dashboard.

HTML

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Skyglass | Citizen Weather Intelligence</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <header>
        <h1>Project Skyglass 🌩️</h1>
        <p>A Decentralized, Tamper-Proof Weather & Earth Intelligence System</p>
    </header>
    <main>
        <h2>Data Registry Log</h2>
        <p>This is an immutable log of all data collected by the system. Each file is secured with a SHA256 hash to guarantee its integrity.</p>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Timestamp (UTC)</th>
                        <th>Data Source</th>
                        <th>File Path</th>
                        <th class="hash-column">SHA256 Integrity Hash</th>
                    </tr>
                </thead>
                <tbody>
                    {% for entry in entries %}
                    <tr>
                        <td>{{ entry['timestamp'] }}</td>
                        <td>{{ entry['data_source'] }}</td>
                        <td>{{ entry['file_path'] }}</td>
                        <td class="hash-cell">{{ entry['sha256_hash'] }}</td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="4">No data has been logged yet. Run 'python skyglass.py fetch' to begin.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </main>
    <footer>
        <p>Local-First, Citizen-Operated. Your Data, Your Eyes.</p>
    </footer>
</body>
</html>

4.7. Viewer CSS: viewer/static/css/style.css
Styling for the dashboard.

CSS

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background-color: #121212;
    color: #e0e0e0;
    margin: 0;
    padding: 2rem;
}

header {
    text-align: center;
    border-bottom: 1px solid #333;
    padding-bottom: 1rem;
    margin-bottom: 2rem;
}

h1 {
    color: #ffffff;
    font-size: 2.5rem;
}

h2 {
    color: #eeeeee;
    border-bottom: 1px solid #444;
    padding-bottom: 0.5rem;
}

.table-container {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
}

th, td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #333;
}

th {
    background-color: #1f1f1f;
    color: #ffffff;
}

tbody tr:hover {
    background-color: #2a2a2a;
}

.hash-cell {
    font-family: "Courier New", Courier, monospace;
    font-size: 0.85rem;
    color: #8a8a8a;
    word-break: break-all;
}

footer {
    text-align: center;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid #333;
    color: #777;
}

4.8. Main Conductor: skyglass.py
The master CLI that orchestrates all system functions.

Python

# skyglass.py

import click
import datetime
from pathlib import Path
from collector import sentinel_api
from registry import logger
from viewer.app import run_viewer

@click.group()
def cli():
    """
    Project Skyglass: A local-first, citizen-operated weather intelligence system.
    """
    pass

@cli.command()
def setup():
    """
    Initializes the database and required directory structure.
    This should be run once before any other commands.
    """
    click.echo("Initializing Project Skyglass environment...")
    Path("data/satellite/sentinel-1").mkdir(parents=True, exist_ok=True)
    logger.setup_database()
    click.secho("Setup complete. Please ensure your API credentials are in a .env file.", fg="green")

@cli.command()
def fetch():
    """
    Fetches the latest Sentinel-1 radar imagery for a predefined area.
    (Defaulting to Asheville, NC region for demonstration).
    """
    click.echo("Fetching data for source: Sentinel-1...")
    
    # Bounding Box for Asheville, NC and surrounding mountains
    asheville_bbox = [-82.9, 35.3, -82.2, 35.8]
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    output_dir = Path("data/satellite/sentinel-1")
    
    file_path = sentinel_api.fetch_sentinel1_data(
        bbox_coords=asheville_bbox,
        start_date=yesterday,
        end_date=today,
        output_path=output_dir
    )
    
    if file_path:
        logger.log_data_entry(file_path, source="Sentinel-1")
    
    click.echo("Fetch operation complete.")

@cli.command()
def view():
    """
    Launches the local web viewer dashboard to display the data log.
    """
    click.echo("Launching Skyglass Viewer...")
    click.echo("Navigate to http://127.0.0.1:5656 in your web browser.")
    click.echo("Press CTRL+C in this terminal to shut down the server.")
    run_viewer()

if __name__ == '__main__':
    cli()

5. Execution and Operational Plan
Installation: Install all required Python libraries.

Bash

pip install -r requirements.txt

Configuration: Create a file named .env in the project root, copy the contents of .env.example into it, and add your Sentinel Hub Client ID and Secret.

System Initialization: Run the setup command. This will create the necessary data directories and initialize the SQLite database.

Bash

python skyglass.py setup

Data Acquisition: Execute the fetch command to download the latest radar imagery for the predefined region. This command can be scheduled to run automatically (e.g., via a cron job).

Bash

python skyglass.py fetch

Data Visualization and Verification: Launch the local dashboard to view the log of collected data. Check the timestamps and SHA256 hashes to verify the integrity and timeliness of your data.

Bash

python skyglass.py view
