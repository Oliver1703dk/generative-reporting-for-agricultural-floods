"""
LLM Report Generator using OpenAI GPT-5
"""
import os
from openai import OpenAI
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

STAKEHOLDER_PROMPTS = {
    "general": {
        "label": "General Overview",
        "system_prompt": (
            "You are an expert environmental monitoring analyst specializing in flood "
            "detection and emergency response. You provide clear, actionable reports "
            "based on sensor data."
        ),
        "sections": [
            "Executive Summary: Brief overview of current flood situation",
            "Critical Alerts: Detailed analysis of Level 2 flood locations with specific sensor readings",
            "Areas of Concern: Analysis of Level 1 suspicious locations",
            "Environmental Analysis: Temperature, humidity, and pressure anomaly patterns",
            "Risk Assessment: Overall flood risk evaluation for the region",
            "Immediate Actions Required: Specific recommendations for emergency response teams",
            "Monitoring Recommendations: Suggested focus areas for continued surveillance",
        ],
    },
    "farmer": {
        "label": "Farmer",
        "system_prompt": (
            "You are an agricultural flood-risk advisor writing for farmers. Focus on "
            "operational summaries: field accessibility, mobility risks on rural roads, "
            "crop and livestock impacts, and practical steps a farmer can take today. "
            "Use plain, jargon-free language."
        ),
        "sections": [
            "Situation Overview: Current flood status in simple terms",
            "Field & Road Accessibility: Which areas are passable and which are not",
            "Crop Impact Assessment: Risks to planted crops and soil saturation levels",
            "Livestock Safety: Flood risks to animals and recommended relocations",
            "Immediate Actions: Practical steps to protect property and livelihood",
            "Short-Term Outlook: What to expect in the next 24-48 hours",
        ],
    },
    "agronomist": {
        "label": "Agronomist",
        "system_prompt": (
            "You are a precision-agriculture analyst writing for agronomists. Provide "
            "analytical reports on soil health impacts, sensor anomaly patterns, water "
            "table changes, and data-driven recommendations for crop management under "
            "flood conditions."
        ),
        "sections": [
            "Data Summary: Statistical overview of sensor readings and anomalies",
            "Soil Health Impact: Moisture saturation, nutrient leaching risks, and erosion patterns",
            "Anomaly Analysis: Temperature, humidity, and pressure deviations with root-cause hypotheses",
            "Crop Vulnerability Assessment: Which crop types and growth stages are most at risk",
            "Drainage & Irrigation Recommendations: Adjustments to water management systems",
            "Monitoring Priorities: Sensors and parameters requiring closer observation",
        ],
    },
    "manager": {
        "label": "Farm Manager/Operator",
        "system_prompt": (
            "You are a fleet and operations analyst writing for farm managers and "
            "operators. Focus on vehicle safety, equipment protection, detection logs, "
            "operational metrics, and workforce scheduling adjustments due to flood "
            "conditions."
        ),
        "sections": [
            "Operations Dashboard: Key metrics at a glance",
            "Vehicle & Equipment Safety: Routes to avoid and equipment relocation needs",
            "Detection Log Summary: Timeline of flood detections and status changes",
            "Workforce Impact: Scheduling adjustments and safety protocols",
            "Asset Protection: Priority actions to safeguard machinery and infrastructure",
            "Recovery Planning: Steps to resume normal operations once conditions improve",
        ],
    },
    "government": {
        "label": "Government Agency",
        "system_prompt": (
            "You are a compliance and disaster-management analyst writing for government "
            "agencies (agriculture, environment, disaster management). Provide formal "
            "compliance overviews with audit trails, regulatory context, and inter-agency "
            "coordination recommendations."
        ),
        "sections": [
            "Executive Briefing: High-level situation assessment for decision-makers",
            "Regulatory Compliance Status: Environmental and safety regulation adherence",
            "Audit Trail: Timestamped detection events and response actions",
            "Affected Area Analysis: Geographic scope and population/infrastructure impact",
            "Inter-Agency Coordination: Recommended actions across departments",
            "Resource Allocation: Suggested deployment of emergency resources",
            "Public Communication: Key messages for public advisories",
        ],
    },
    "insurance": {
        "label": "Insurance Company",
        "system_prompt": (
            "You are a risk and damage assessment analyst writing for insurance "
            "companies. Provide structured damage assessments with supporting sensor "
            "evidence, loss estimates, affected asset inventories, and claim-relevant "
            "documentation."
        ),
        "sections": [
            "Incident Summary: Event overview with timestamps and severity classification",
            "Damage Assessment: Sensor-backed evidence of flood impact by location",
            "Affected Asset Inventory: Properties, infrastructure, and crops in flood zones",
            "Risk Exposure Analysis: Current and projected loss estimates",
            "Evidence Documentation: Sensor readings, anomaly data, and detection confidence scores",
            "Claim Recommendations: Suggested claim categories and supporting data references",
        ],
    },
}


def generate_report(sensors: List[Dict], stakeholder: str = "general") -> str:
    """Generate a comprehensive flood monitoring report using GPT-5"""
    config = STAKEHOLDER_PROMPTS.get(stakeholder, STAKEHOLDER_PROMPTS["general"])

    # Prepare data summary for the LLM
    total_sensors = len(sensors)
    flood_count = sum(1 for s in sensors if s.get('prediction') == 2)
    suspicious_count = sum(1 for s in sensors if s.get('prediction') == 1)
    normal_count = sum(1 for s in sensors if s.get('prediction') == 0)

    # Prepare detailed sensor information
    sensor_details = []
    for sensor in sensors:
        detail = {
            'camera_id': sensor.get('camera_id'),
            'location': sensor.get('location'),
            'classification': sensor.get('prediction'),
            'combined_score': sensor.get('scores', {}).get('combined_score', 0),
            'temperature': sensor.get('sensor_data', {}).get('temperature'),
            'humidity': sensor.get('sensor_data', {}).get('humidity'),
            'pressure': sensor.get('sensor_data', {}).get('pressure'),
            'delta_temp': sensor.get('sensor_anomalies', {}).get('delta_temperature'),
            'delta_humidity': sensor.get('sensor_anomalies', {}).get('delta_humidity'),
            'delta_pressure': sensor.get('sensor_anomalies', {}).get('delta_pressure'),
        }
        sensor_details.append(detail)

    # Build numbered sections list from config
    sections_text = "\n".join(
        f"{i}. **{section}**" for i, section in enumerate(config["sections"], 1)
    )

    # Craft the prompt using best practices
    prompt = f"""Generate a report tailored for: **{config['label']}**

Based on the following real-time sensor data from Fyn Island, Denmark.

**REPORT REQUIREMENTS:**
- Use clear headings and sections
- Provide actionable insights and recommendations
- Highlight critical areas requiring immediate attention
- Include statistical analysis
- Maintain professional tone
- Format in markdown for readability

**DATA SUMMARY:**
- Total Monitoring Stations: {total_sensors}
- Critical Flood Alerts (Level 2): {flood_count}
- Suspicious Areas (Level 1): {suspicious_count}
- Normal Conditions (Level 0): {normal_count}
- Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**DETAILED SENSOR DATA:**
{format_sensor_data_for_prompt(sensor_details)}

**GENERATE A REPORT WITH THE FOLLOWING SECTIONS:**

{sections_text}

Be specific, data-driven, and actionable. Include actual sensor readings and coordinates in your analysis."""

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini-2025-08-07",
            messages=[
                {"role": "system", "content": config["system_prompt"]},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more focused, factual output
            max_tokens=2500
        )

        report = response.choices[0].message.content
        return report

    except Exception as e:
        return f"**Error Generating Report**\n\nAn error occurred: {str(e)}\n\nPlease check your API key and connection."


def format_sensor_data_for_prompt(sensor_details: List[Dict]) -> str:
    """Format sensor data in a clean way for the LLM"""
    formatted = []

    for i, sensor in enumerate(sensor_details, 1):
        classification_label = {0: "Normal", 1: "Suspicious", 2: "FLOOD"}.get(sensor['classification'], "Unknown")

        formatted.append(f"""
Camera {sensor['camera_id']} (Location: {sensor['location']}):
  - Classification: {classification_label} (Level {sensor['classification']})
  - Flooding Score: {sensor['combined_score']:.3f}
  - Temperature: {sensor['temperature']}°C (Δ {sensor['delta_temp']}°C)
  - Humidity: {sensor['humidity']}% (Δ {sensor['delta_humidity']}%)
  - Pressure: {sensor['pressure']} hPa (Δ {sensor['delta_pressure']} hPa)
""")

    return "\n".join(formatted)


def format_report_for_download(report: str) -> str:
    """Convert markdown report to clean readable text"""
    import re

    # Remove markdown formatting
    clean_report = report

    # Convert headers (### -> section titles)
    clean_report = re.sub(r'^#{1,6}\s+(.+)$', r'\n\n\1\n' + '=' * 60, clean_report, flags=re.MULTILINE)

    # Remove bold/italic markers
    clean_report = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_report)
    clean_report = re.sub(r'\*(.+?)\*', r'\1', clean_report)

    # Convert bullet points
    clean_report = re.sub(r'^[\*\-]\s+', '  • ', clean_report, flags=re.MULTILINE)

    # Clean up multiple newlines
    clean_report = re.sub(r'\n{3,}', '\n\n', clean_report)

    return clean_report.strip()


def save_report_to_file(report: str, filename: str = "flood_report.txt") -> str:
    """Save the report to a downloadable file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename_with_timestamp = f"flood_report_{timestamp}.txt"

    # Convert markdown to clean text
    clean_report = format_report_for_download(report)

    # Add header
    header = f"""
{'=' * 70}
FLOOD MONITORING REPORT - FYN ISLAND, DENMARK
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 70}

"""

    with open(filename_with_timestamp, 'w', encoding='utf-8') as f:
        f.write(header + clean_report)

    return filename_with_timestamp
