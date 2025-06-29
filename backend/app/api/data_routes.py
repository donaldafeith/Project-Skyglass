from flask import Blueprint, jsonify
from app.models import DataLog
from sqlalchemy import desc

data_bp = Blueprint('data_bp', __name__)

@data_bp.route('/status', methods=['GET'])
def status():
    return jsonify(message="Skyglass Backend Service is Active")

@data_bp.route('/latest/<string:source>', methods=['GET'])
def get_latest_data(source):
    entry = DataLog.query.filter_by(source=source, success=True).order_by(desc(DataLog.timestamp)).first()
    if entry:
        return jsonify(entry.data)
    last_error = DataLog.query.filter_by(source=source, success=False).order_by(desc(DataLog.timestamp)).first()
    if last_error:
        return jsonify({"error": f"Last attempt failed: {last_error.error_message}"}), 500
    return jsonify({"error": "No data found. The scheduler may not have run yet."}), 404
