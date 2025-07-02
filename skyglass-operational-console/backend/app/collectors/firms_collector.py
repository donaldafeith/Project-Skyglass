import requests
import pandas as pd
from io import StringIO
from config import Config

def fetch_data():
    if not Config.FIRMS_API_KEY:
        return {"error": "FIRMS_API_KEY not configured"}
    url = f"https://firms.modaps.eosdis.nasa.gov/api/v1/nrt/viirs-snpp-j1/csv/{Config.FIRMS_API_KEY}/world/1"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        if not response.text:
            return {"type": "FeatureCollection", "features": []}
        df = pd.read_csv(StringIO(response.text))
        features = [{
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [row['longitude'], row['latitude']]},
            "properties": {
                "brightness": row['bright_ti4'],
                "confidence": row['confidence'],
                "frp": row['frp'],
                "acq_time": row['acq_time']
            }
        } for _, row in df.iterrows()]
        return {"type": "FeatureCollection", "features": features}
    except Exception as e:
        return {"error": f"FIRMS Collector Error: {str(e)}"}
