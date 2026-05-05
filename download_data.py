"""
Download Dataset Script
=======================
Downloads the full Olist Brazilian E-Commerce Public Dataset from Kaggle
using kagglehub and copies all CSV files into the local `data/` directory.

Prerequisites:
  - A Kaggle account with an API token configured.
      See: https://www.kaggle.com/docs/api#authentication
  - kagglehub installed:  pip install kagglehub

Usage:
    python download_data.py
"""

import kagglehub
import os
import shutil
from pathlib import Path


DATASET_SLUG = "olistbr/brazilian-ecommerce"

# Destination: data/ folder at the project root
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"


def download_and_copy() -> None:
    """Download the dataset from Kaggle and copy CSVs to data/."""

    print("=" * 60)
    print("DOWNLOADING OLIST BRAZILIAN E-COMMERCE DATASET")
    print("=" * 60)
    print(f"Dataset : {DATASET_SLUG}")
    print(f"Target  : {DATA_DIR}\n")

    # ── Download (cached after first run) ─────────────────────────
    print("Fetching dataset via kagglehub (may take a moment the first time)...")
    path = kagglehub.dataset_download(DATASET_SLUG)
    print(f"\nPath to dataset files: {path}\n")

    # ── Copy CSVs to data/ ────────────────────────────────────────
    DATA_DIR.mkdir(exist_ok=True)

    src_path = Path(path)
    csv_files = list(src_path.glob("*.csv"))

    if not csv_files:
        # The download may unpack into a single sub-folder
        sub_dirs = [d for d in src_path.iterdir() if d.is_dir()]
        if sub_dirs:
            csv_files = list(sub_dirs[0].glob("*.csv"))

    if not csv_files:
        print("WARNING: No CSV files found in the downloaded path. Please check manually:")
        print(f"  {path}")
        return

    print(f"Found {len(csv_files)} CSV file(s). Copying to {DATA_DIR} ...\n")
    for csv_file in sorted(csv_files):
        dest = DATA_DIR / csv_file.name
        shutil.copy2(csv_file, dest)
        size_kb = dest.stat().st_size / 1024
        print(f"  [OK]  {csv_file.name:55s}  ({size_kb:,.1f} KB)")

    print("\n" + "=" * 60)
    print("DATASET READY")
    print("=" * 60)
    print(f"All files have been copied to: {DATA_DIR}")
    print("\nExpected files:")
    expected = [
        "olist_customers_dataset.csv",
        "olist_geolocation_dataset.csv",
        "olist_order_items_dataset.csv",
        "olist_order_payments_dataset.csv",
        "olist_order_reviews_dataset.csv",
        "olist_orders_dataset.csv",
        "olist_products_dataset.csv",
        "olist_sellers_dataset.csv",
        "product_category_name_translation.csv",
    ]
    for fname in expected:
        status = "[OK]" if (DATA_DIR / fname).exists() else "[!!] MISSING"
        print(f"  {status}  {fname}")


if __name__ == "__main__":
    download_and_copy()
