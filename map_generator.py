"""
Map generation module using Folium
"""
import folium
from folium import IFrame
import os
from typing import List, Dict
from config import FYN_ISLAND_CENTER, DEFAULT_ZOOM, CLASSIFICATION, DATA_DIR

def create_base_map() -> folium.Map:
    """Create the base map centered on Fyn Island"""
    flood_map = folium.Map(
        location=FYN_ISLAND_CENTER,
        zoom_start=DEFAULT_ZOOM,
        tiles='OpenStreetMap',
        control_scale=True
    )
    return flood_map

def get_marker_color(prediction: int) -> str:
    """Get marker color based on prediction level"""
    return CLASSIFICATION.get(prediction, CLASSIFICATION[0])['color']

def create_popup_html(sensor: Dict) -> str:
    """Create HTML content for popup card"""
    prediction = sensor.get('prediction', 0)
    classification_info = CLASSIFICATION.get(prediction, CLASSIFICATION[0])

    scores = sensor.get('scores', {})
    sensor_data = sensor.get('sensor_data', {})
    sensor_baseline = sensor.get('sensor_baseline', {})
    sensor_anomalies = sensor.get('sensor_anomalies', {})

    # Around line 35-45 in create_popup_html function
    image_html = ''
    image_file = sensor.get('image_file', '')

    if image_file:
        # Use ABSOLUTE URL for iframe compatibility
        image_url = f'http://127.0.0.1:8050/data/video_results_1/{image_file}'
        image_html = f'<img src="{image_url}" style="width:100%; max-width:300px; border-radius:8px; margin-bottom:10px;">'
    else:
        image_html = '<p style="color:#999; font-style:italic;">Image not available</p>'

    html = f'''<div style="font-family: Arial, sans-serif; width: 320px; padding: 15px;">
<h3 style="margin:0 0 10px 0; color:#333; border-bottom: 3px solid {classification_info["color"]}; padding-bottom:8px;">
Camera {sensor.get('camera_id', 'Unknown')}
</h3>
{image_html}
<div style="background: {classification_info["color"]}; color: white; padding: 8px; border-radius: 5px; margin-bottom: 12px; text-align: center; font-weight: bold;">
Classification: {classification_info["label"]} ({prediction})
</div>
<div style="margin-bottom: 12px;">
<strong style="color:#0066cc;">📊 Flooding Score</strong>
<div style="background:#f8f9fa; padding:8px; border-radius:5px; margin-top:5px;">
<div>Combined: <strong>{scores.get('combined_score', 0):.3f}</strong></div>
<div>Image Score: {scores.get('image_score', 0):.3f}</div>
<div>Sensor Boost: {scores.get('sensor_boost', 0):.3f}</div>
<div>Prediction: {scores.get('sensor_prediction', 'N/A')}</div>
</div>
</div>
<div style="margin-bottom: 12px;">
<strong style="color:#0066cc;">🌡️ Sensor Data</strong>
<div style="background:#f8f9fa; padding:8px; border-radius:5px; margin-top:5px;">
<div>Temperature: <strong>{sensor_data.get('temperature', 0):.1f}°C</strong> (baseline: {sensor_baseline.get('temperature_baseline', 0):.1f}°C)</div>
<div>Humidity: <strong>{sensor_data.get('humidity', 0):.1f}%</strong> (baseline: {sensor_baseline.get('humidity_baseline', 0):.1f}%)</div>
<div>Pressure: <strong>{sensor_data.get('pressure', 0):.1f} hPa</strong> (baseline: {sensor_baseline.get('pressure_baseline', 0):.1f} hPa)</div>
</div>
</div>
<div>
<strong style="color:#0066cc;">⚠️ Anomalies (Δ)</strong>
<div style="background:#fff3cd; padding:8px; border-radius:5px; margin-top:5px;">
<div>Δ Temperature: <strong>{sensor_anomalies.get('delta_temperature', 0):.1f}°C</strong></div>
<div>Δ Humidity: <strong>{sensor_anomalies.get('delta_humidity', 0):.1f}%</strong></div>
<div>Δ Pressure: <strong>{sensor_anomalies.get('delta_pressure', 0):.1f} hPa</strong></div>
</div>
</div>
<div style="margin-top:10px; font-size:11px; color:#666;">
Timestamp: {sensor.get('timestamp', 'N/A')}
</div>
</div>'''

    return html

def add_sensor_markers(flood_map: folium.Map, sensors: List[Dict]) -> folium.Map:
    """Add markers for all sensors to the map"""
    for sensor in sensors:
        location = sensor.get('location')
        if not location:
            continue

        prediction = sensor.get('prediction', 0)
        color = get_marker_color(prediction)

        popup_html = create_popup_html(sensor)
        iframe = IFrame(html=popup_html, width=350, height=550)
        popup = folium.Popup(iframe, max_width=350)

        folium.Marker(
            location=location,
            popup=popup,
            icon=folium.Icon(color=color, icon='tint', prefix='fa'),
            tooltip=f"Camera {sensor.get('camera_id', 'Unknown')} - Click for details"
        ).add_to(flood_map)

    return flood_map


def generate_map(sensors: List[Dict], output_file: str = 'flood_map.html') -> str:
    """Generate complete map with all sensors"""
    flood_map = create_base_map()
    flood_map = add_sensor_markers(flood_map, sensors)

    # Add user location marker (Odense, Denmark)
    user_location = [55.4038, 10.4024]  # Odense coordinates
    folium.Marker(
        location=user_location,
        popup=folium.Popup("📍 Your Location<br>Odense, Denmark", max_width=200),
        icon=folium.Icon(color='blue', icon='user', prefix='fa'),
        tooltip="Your Location"
    ).add_to(flood_map)

    flood_map.save(output_file)
    return output_file
