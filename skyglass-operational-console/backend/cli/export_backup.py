import os
import shutil
from datetime import datetime


def export_backup():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_path = os.path.join(project_root, 'app.db')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    backup_root = os.path.join(os.path.expanduser("~"), f'skyglass_backup_{timestamp}')
    os.makedirs(backup_root, exist_ok=True)

    if os.path.exists(db_path):
        shutil.copy(db_path, os.path.join(backup_root, 'app.db'))
        print(f"Database backed up to {backup_root}")
    else:
        print(f"Database file not found at {db_path}, skipping backup.")

if __name__ == '__main__':
    export_backup()
