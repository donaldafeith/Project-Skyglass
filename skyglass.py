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
