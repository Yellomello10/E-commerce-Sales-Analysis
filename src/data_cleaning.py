"""
Data Cleaning Module

Handles loading, cleaning, and merging of e-commerce datasets.
"""

import pandas as pd
import os
from pathlib import Path


def load_data(data_dir: str) -> dict:
    """
    Load all CSV datasets from the specified directory.

    Args:
        data_dir: Path to directory containing CSV files

    Returns:
        Dictionary with DataFrames for each dataset
    """
    datasets = {
        'orders': 'olist_orders_dataset.csv',
        'customers': 'olist_customers_dataset.csv',
        'order_items': 'olist_order_items_dataset.csv',
        'payments': 'olist_order_payments_dataset.csv',
        'products': 'olist_products_dataset.csv',
        'sellers': 'olist_sellers_dataset.csv',
        'category_translation': 'olist_products_category_name_translation.csv'
    }

    loaded_data = {}

    for name, filename in datasets.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            loaded_data[name] = pd.read_csv(filepath)
            print(f"Loaded {name}: {loaded_data[name].shape}")
        else:
            print(f"Warning: {filename} not found at {filepath}")
            loaded_data[name] = None

    return loaded_data


def clean_data(data: dict) -> dict:
    """
    Clean all datasets by handling missing values, converting dates, and removing duplicates.

    Args:
        data: Dictionary of DataFrames from load_data()

    Returns:
        Dictionary of cleaned DataFrames
    """
    cleaned = {}

    # Clean orders dataset
    if data['orders'] is not None:
        cleaned['orders'] = clean_orders(data['orders'])

    # Clean customers dataset
    if data['customers'] is not None:
        cleaned['customers'] = clean_customers(data['customers'])

    # Clean order items dataset
    if data['order_items'] is not None:
        cleaned['order_items'] = clean_order_items(data['order_items'])

    # Clean payments dataset
    if data['payments'] is not None:
        cleaned['payments'] = clean_payments(data['payments'])

    # Clean products dataset
    if data['products'] is not None:
        cleaned['products'] = clean_products(data['products'])

    # Clean sellers dataset
    if data['sellers'] is not None:
        cleaned['sellers'] = clean_sellers(data['sellers'])

    # Clean category translation
    if data['category_translation'] is not None:
        cleaned['category_translation'] = data['category_translation'].drop_duplicates()

    print(f"\nCleaned {len(cleaned)} datasets")
    return cleaned


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Clean orders dataset: handle dates and missing values."""
    df = df.copy()

    # Convert date columns to datetime
    date_cols = ['order_purchase_timestamp', 'order_approved_at',
                 'order_delivered_carrier_date', 'order_delivered_customer_date',
                 'order_estimated_delivery_date']

    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Drop rows with missing purchase timestamp (critical field)
    df = df.dropna(subset=['order_purchase_timestamp'])

    # Remove duplicates
    df = df.drop_duplicates(subset=['order_id'])

    return df


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Clean customers dataset: handle missing values."""
    df = df.copy()

    # Remove duplicates
    df = df.drop_duplicates(subset=['customer_id'])

    # Fill missing geolocation data with mode values
    if 'customer_state' in df.columns:
        df['customer_state'] = df['customer_state'].fillna(df['customer_state'].mode()[0])
    if 'customer_city' in df.columns:
        df['customer_city'] = df['customer_city'].fillna(df['customer_city'].mode()[0])

    return df


def clean_order_items(df: pd.DataFrame) -> pd.DataFrame:
    """Clean order items dataset."""
    df = df.copy()

    # Remove duplicates
    df = df.drop_duplicates()

    # Ensure price is numeric
    if 'price' in df.columns:
        df['price'] = pd.to_numeric(df['price'], errors='coerce')

    # Remove rows with invalid prices
    df = df[df['price'] > 0]

    return df


def clean_payments(df: pd.DataFrame) -> pd.DataFrame:
    """Clean payments dataset."""
    df = df.copy()

    # Ensure payment value is numeric
    if 'payment_value' in df.columns:
        df['payment_value'] = pd.to_numeric(df['payment_value'], errors='coerce')

    # Remove invalid payments
    df = df[df['payment_value'] > 0]

    return df


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """Clean products dataset."""
    df = df.copy()

    # Remove duplicates
    df = df.drop_duplicates(subset=['product_id'])

    # Fill missing category names with 'unknown'
    if 'product_category_name' in df.columns:
        df['product_category_name'] = df['product_category_name'].fillna('unknown')

    return df


def clean_sellers(df: pd.DataFrame) -> pd.DataFrame:
    """Clean sellers dataset."""
    df = df.copy()

    # Remove duplicates
    df = df.drop_duplicates(subset=['seller_id'])

    return df


def merge_data(cleaned: dict) -> pd.DataFrame:
    """
    Merge all cleaned datasets into a single DataFrame.

    Args:
        cleaned: Dictionary of cleaned DataFrames

    Returns:
        Merged DataFrame with all data combined
    """
    # Start with orders as the base
    df = cleaned['orders'].copy()

    # Merge with customers
    if 'customers' in cleaned and cleaned['customers'] is not None:
        df = df.merge(cleaned['customers'], on='customer_id', how='left')

    # Merge with order items
    if 'order_items' in cleaned and cleaned['order_items'] is not None:
        df = df.merge(cleaned['order_items'], on='order_id', how='left')

    # Merge with payments
    if 'payments' in cleaned and cleaned['payments'] is not None:
        df = df.merge(cleaned['payments'], on='order_id', how='left')

    # Merge with products
    if 'products' in cleaned and cleaned['products'] is not None:
        df = df.merge(cleaned['products'], on='product_id', how='left')

    # Merge with sellers
    if 'sellers' in cleaned and cleaned['sellers'] is not None:
        df = df.merge(cleaned['sellers'], on='seller_id', how='left')

    # Merge with category translation
    if 'category_translation' in cleaned and cleaned['category_translation'] is not None:
        df = df.merge(
            cleaned['category_translation'],
            left_on='product_category_name',
            right_on='product_category_name_english',
            how='left',
            suffixes=('', '_translated')
        )

    print(f"\nMerged dataset shape: {df.shape}")
    print(f"Total records: {len(df):,}")

    return df


def save_processed_data(df: pd.DataFrame, output_path: str) -> None:
    """
    Save the processed DataFrame to CSV.

    Args:
        df: Processed DataFrame
        output_path: Path to save the CSV file
    """
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df.to_csv(output_path, index=False)
    print(f"Saved processed data to {output_path}")
