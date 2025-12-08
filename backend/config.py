"""Configuration settings for the NBFC Loan System"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Mock data path
MOCK_DATA_PATH = BASE_DIR / "mock_data.json"

# File upload settings
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Sanction letter output - Secure storage for generated sanction letters
SANCTION_DIR = BASE_DIR / "data" / "sanction_letters"
SANCTION_DIR.mkdir(parents=True, exist_ok=True)

# Business rules
MIN_CREDIT_SCORE = 700
MAX_EMI_TO_SALARY_RATIO = 0.50  # 50%
PRE_APPROVED_MULTIPLIER = 2  # Can request up to 2x pre-approved limit with salary slip

# Interest rates (annual %)
INTEREST_RATES = {
    "excellent": 10.5,  # Credit score >= 800
    "good": 11.5,       # Credit score >= 750
    "fair": 12.5,       # Credit score >= 700
    "default": 13.5
}

# Tenure options (months)
TENURE_OPTIONS = [12, 24, 36, 48, 60]

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000
