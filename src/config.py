import os

# Gemini configuration
MODEL_NAME = "gemini-2.5-flash"
API_KEY = os.environ.get("GEMINI_API_KEY")

# Directory paths
DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset")
DEFAULT_OUTPUT_EXCEL = os.path.join(os.path.dirname(os.path.dirname(__file__)), "specbook_output_v2.xlsx")
DEFAULT_OUTPUT_CSV = os.path.join(os.path.dirname(os.path.dirname(__file__)), "specbook_output_v2.csv")
DEFAULT_OUTPUT_JSON = os.path.join(os.path.dirname(os.path.dirname(__file__)), "specbook_output_v2.json")
GROUND_TRUTH_EXCEL = os.path.join(DATASET_DIR, "specboook.xlsx")

# Web assets path
WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
