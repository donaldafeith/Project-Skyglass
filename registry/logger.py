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
