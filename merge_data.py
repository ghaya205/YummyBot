# merge_data.py
import os
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# FORCE CAPITALIZED "Data" FOLDER
DATA_DIR = os.path.join(BASE_DIR, "Data")

KAGGLE_CLEAN_PATH = os.path.join(DATA_DIR, "recipes_clean.json")
TUNISIAN_PATH = os.path.join(DATA_DIR, "tunisian_receipe.json")
FINAL_OUTPUT_PATH = os.path.join(DATA_DIR, "recipes_final.json")

print("Checking required source files...")
if not os.path.exists(KAGGLE_CLEAN_PATH):
    print(f"❌ Missing intermediate data! Run cleandata.py first.")
elif not os.path.exists(TUNISIAN_PATH):
    print(f"❌ Missing file! Make sure 'tunisian_receipe.json' is inside your {DATA_DIR} folder.")
else:
    # 1. Load clean international items
    print(f"Loading data from: {KAGGLE_CLEAN_PATH}")
    kaggle_df = pd.read_json(KAGGLE_CLEAN_PATH)
    kaggle_data = kaggle_df.to_dict(orient="records")

    # 2. Load custom local Tunisian recipes
    print(f"Loading data from: {TUNISIAN_PATH}")
    with open(TUNISIAN_PATH, encoding="utf-8") as f:
        tunisian_data = json.load(f)

    # 3. Structural merge action
    final_data = kaggle_data + tunisian_data

    # 4. Save compilation output
    with open(FINAL_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print("\n--- Summary ---")
    print(f"🌍 Kaggle recipes added: {len(kaggle_data)}")
    print(f"🇹🇳 Tunisian recipes added: {len(tunisian_data)}")
    print(f"🚀 Total combined database size: {len(final_data)} recipes")
    print(f"✅ Magic done! Successfully created: {FINAL_OUTPUT_PATH}")