from app.extensions import db
from app.models import DataLog
import json
import hashlib


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
