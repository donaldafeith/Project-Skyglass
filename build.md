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
The project is organized with the following directory structure to ensure modularity and clarity.

```
/project_skyglass/
├── build.md
├── requirements.txt
├── .env.example
├── skyglass.py
├── collector/
│   ├── __init__.py
│   └── sentinel_api.py
├── registry/
│   ├── __init__.py
│   ├── logger.py
│   └── skyglass_log.db
├── viewer/
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
└── data/
    └── satellite/
        └── sentinel-1/
```

4. Execution and Operational Plan

Installation:
```bash
pip install -r requirements.txt
```

Configuration: Create a file named `.env` in the project root, copy the contents of `.env.example` into it, and add your Sentinel Hub Client ID and Secret.

System Initialization:
```bash
python skyglass.py setup
```

Data Acquisition:
```bash
python skyglass.py fetch
```

Data Visualization and Verification:
```bash
python skyglass.py view
```
