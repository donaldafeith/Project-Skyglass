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
