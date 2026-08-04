import os
from dotenv import load_dotenv

# This reads your .env file and loads the API key
load_dotenv()

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL          = "gpt-4o"
TEMPERATURE    = 0        # 0 means consistent, not random
MAX_TOKENS     = 1000

# How many times to repeat each test (for reliability)
RUNS_PER_CONFIG = 5

# Paths
GHRB_PATH  = "data/ghrb"
RESULTS_DB = "results/results.db"
TEMP_DIR   = "temp"