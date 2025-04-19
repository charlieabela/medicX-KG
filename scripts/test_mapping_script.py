# test_mapping_script.py

"""
Simple test script to verify that the medicX-KG mapping scripts are installed and working.
Run this after setting up /scripts and /data folders locally.
"""

import os
import sys

# Add the scripts directory to path if running from root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from MappingHelperMethods import clean_active_ingredient, split_active_ingredients
    print("✅ MappingHelperMethods imported successfully.")

    sample_text = "Paracetamol + Caffeine"
    cleaned = clean_active_ingredient(sample_text)
    split = split_active_ingredients(sample_text)

    print(f"Original: {sample_text}")
    print(f"Cleaned: {cleaned}")
    print(f"Split: {split}")

except ImportError as e:
    print("Error: Could not import helper methods.")
    print(str(e))

try:
    from map_medicinesAuthority import ontology
    print("map_medicinesAuthority script imported successfully.")
    print(f"Ontology base URI: {ontology}")
except ImportError as e:
    print("Error: Could not import map_medicinesAuthority script.")
    print(str(e))

print("\nIf you see two messages, your local setup is ready!")
