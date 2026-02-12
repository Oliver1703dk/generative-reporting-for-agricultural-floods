"""
Main entry point for the Flood Monitoring Dashboard
Run this file to start the dashboard
"""
from data_loader import load_all_sensors
from map_generator import generate_map
from dashboard import create_dashboard_app
import flask
import os
from config import DATA_DIR


def main():
    """Main function to run the dashboard"""
    print("🌊 Starting Flood Monitoring Dashboard...")

    # Load sensor data from JSON files
    print("📂 Loading sensor data...")
    sensors = load_all_sensors(max_sensors=25)

    if not sensors:
        print("❌ Error: No sensor data found. Make sure JSON files (1.json, 2.json, ...) are in the same directory.")
        return

    print(f"✓ Loaded {len(sensors)} sensors")

    # Generate map
    print("🗺️  Generating map...")
    map_file = generate_map(sensors, output_file='flood_map.html')
    print(f"✓ Map generated: {map_file}")

    # Create and run dashboard
    print("🚀 Starting dashboard server...")
    app = create_dashboard_app(sensors, map_file)

    @app.server.route('/data/video_results_1/<path:filename>')
    def serve_images(filename):
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(current_dir, 'data', 'video_results_1')
        return flask.send_from_directory(data_path, filename)

    @app.server.route('/map')
    def serve_map():
        return flask.send_file('flood_map.html')

    print("\n" + "=" * 60)
    print("✓ Dashboard is running!")
    print("📍 Open your browser and go to: http://127.0.0.1:8050")
    print("=" * 60 + "\n")

    app.run_server(debug=True, host='127.0.0.1', port=8050)


if __name__ == "__main__":
    main()
