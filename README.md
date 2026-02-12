# Flood Monitoring Dashboard - Fyn Island, Denmark

An interactive flood monitoring dashboard that combines edge-based sensor data with AI-driven stakeholder reports. Built as a research prototype for the **ICSA 2026 SAGAI Workshop**, it visualizes real-time flood classifications on an interactive map and generates tailored LLM reports for different stakeholders (farmers, agronomists, government agencies, etc.).

## Features

- **Interactive Map** — Color-coded pins (red/orange/green) on Fyn Island showing flood, suspicious, and normal sensor readings. Click any pin for detailed sensor data and detection images.
- **Statistics Dashboard** — Live counts of flood alerts, suspicious areas, and normal conditions.
- **Stakeholder-Specific AI Reports** — Select a stakeholder type from the dropdown and generate a GPT-4 report tailored to their needs:
  | Stakeholder | Focus |
  |---|---|
  | General Overview | Executive summary, risk assessment, recommendations |
  | Farmer | Field accessibility, crop impact, livestock safety |
  | Agronomist | Soil health, anomaly patterns, drainage recommendations |
  | Farm Manager/Operator | Vehicle safety, detection logs, workforce scheduling |
  | Government Agency | Compliance, audit trails, inter-agency coordination |
  | Insurance Company | Damage assessment, evidence documentation, loss estimates |
- **Report Download** — Generated reports are saved as timestamped `.txt` files.

## Project Structure

```
.
├── main.py              # Entry point — loads data, generates map, starts dashboard
├── config.py            # Configuration (map center, colors, data paths)
├── data_loader.py       # Reads JSON sensor data from data/ directory
├── map_generator.py     # Creates Folium map with interactive markers
├── dashboard.py         # Dash web app with UI and callbacks
├── llm_report.py        # OpenAI integration and stakeholder prompt configs
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not committed)
└── data/
    └── video_results_1/ # Sensor JSON files (1.json–25.json) and detection images
```

## Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)

## Setup

1. **Clone the repository** and navigate to the project directory.

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables** — create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

4. **Verify sensor data** exists in `data/video_results_1/` (JSON files numbered `1.json` through `25.json` with corresponding `.png` images).

## Running

```bash
python main.py
```

Open your browser to **http://127.0.0.1:8050**.

## How It Works

```
JSON sensor data  →  data_loader.py  →  map_generator.py (Folium map)
                                     →  dashboard.py (Dash UI)
                                         └─ llm_report.py (GPT-4) → stakeholder report
```

1. `data_loader.py` reads sensor JSON files containing temperature, humidity, pressure readings, anomaly deltas, and flood classifications (0 = Normal, 1 = Suspicious, 2 = Flood).
2. `map_generator.py` plots each sensor on an interactive Folium map of Fyn Island with color-coded markers and popup details.
3. `dashboard.py` serves a Dash web app embedding the map, statistics cards, and a report generation UI.
4. When the user selects a stakeholder and clicks **Generate AI Report**, `llm_report.py` sends the sensor data with a stakeholder-tailored prompt to GPT-4 and displays the result in a modal.

## Tech Stack

- [Dash](https://dash.plotly.com/) + [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) — Web UI
- [Folium](https://python-visualization.github.io/folium/) — Interactive mapping
- [OpenAI API](https://platform.openai.com/docs) (GPT-4) — Report generation
- [python-dotenv](https://github.com/theskumar/python-dotenv) — Environment variable management

## Data Format

Each sensor JSON file contains:

| Field | Description |
|---|---|
| `camera_id` | Sensor identifier |
| `location` | `[latitude, longitude]` |
| `sensor_data` | Temperature (C), humidity (%), pressure (hPa) |
| `sensor_anomalies` | Delta values from baseline |
| `prediction` | Classification: `0` Normal, `1` Suspicious, `2` Flood |
| `scores.combined_score` | Weighted flood probability (0.0–1.0) |
