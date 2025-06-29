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
