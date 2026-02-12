"""
Configuration file for the Flood Monitoring Dashboard
"""

# Map Configuration
FYN_ISLAND_CENTER = [55.4038, 10.4024]
DEFAULT_ZOOM = 10

# Data Configuration
JSON_FILES_PATTERN = "{}.json"
IMAGE_FILES_PATTERN = "{}.png"
DATA_DIR = "data/video_results_1"


# Classification levels
CLASSIFICATION = {
    0: {"label": "No Flood", "color": "green"},
    1: {"label": "Suspicious", "color": "orange"},
    2: {"label": "Flood", "color": "red"}
}

# Dashboard styling
COLORS = {
    "background": "#f8f9fa",
    "card": "#ffffff",
    "primary": "#0066cc",
    "text": "#333333",
    "border": "#dee2e6"
}
