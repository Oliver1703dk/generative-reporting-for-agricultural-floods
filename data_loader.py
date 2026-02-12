"""
Data loader module for reading JSON files and extracting sensor data
"""
import json
import os
from typing import Dict, List, Optional
from config import DATA_DIR

def load_json_file(filename: str) -> Optional[Dict]:
    """Load a JSON file and return its contents"""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {filepath} not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: {filepath} is not valid JSON")
        return None

def extract_location(data: Dict) -> Optional[tuple]:
    """Extract latitude and longitude from JSON data"""
    if not data or 'metadata' not in data:
        return None

    location_str = data['metadata'].get('location')
    if not location_str:
        return None

    try:
        lat, lon = map(float, location_str.split(', '))
        return (lat, lon)
    except (ValueError, AttributeError):
        return None

def extract_sensor_data(data: Dict) -> Dict:
    """Extract all relevant sensor and classification data"""
    if not data:
        return {}

    metadata = data.get('metadata', {})
    classification = data.get('classification_result', {})

    return {
        'location': extract_location(data),
        'timestamp': metadata.get('timestamp', 'N/A'),
        'camera_id': metadata.get('camera_id', 'Unknown'),
        'sensor_baseline': metadata.get('sensor_baseline', {}),
        'sensor_data': metadata.get('sensor_data', {}),
        'sensor_anomalies': metadata.get('sensor_anomalies', {}),
        'prediction': classification.get('prediction', 0),
        'scores': classification.get('scores', {}),
        'state': classification.get('state', 'Unknown')
    }

def load_all_sensors(max_sensors: int = 25) -> List[Dict]:
    """Load all available sensor JSON files (1.json, 2.json, ...)"""
    sensors = []

    if not os.path.exists(DATA_DIR):
        print(f"Error: Data directory '{DATA_DIR}' does not exist!")
        return sensors

    for i in range(1, max_sensors + 1):
        filename = f"{i}.json"
        data = load_json_file(filename)

        if data:
            sensor_info = extract_sensor_data(data)
            sensor_info['id'] = i
            sensor_info['image_file'] = f"{i}.png"
            sensors.append(sensor_info)
        else:
            if i == 1:
                break
            continue

    return sensors
