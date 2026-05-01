"""
Sample Data Generator

Generates sample e-commerce data for testing the analysis pipeline
when the actual Kaggle dataset is not available.

Run this script to create sample data in the data/ directory.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)


def generate_sample_data(output_dir: str, num_orders: int = 5000) -> None:
    """
    Generate sample e-commerce datasets.

    Args:
        output_dir: Directory to save CSV files
        num_orders: Number of orders to generate
    """
    os.makedirs(output_dir, exist_ok=True)

    print(f"Generating sample data with {num_orders:,} orders...")

    # Date range for the data
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    # Generate order IDs
    order_ids = [f"ORD_{i:06d}" for i in range(1, num_orders + 1)]

    # ========== CUSTOMERS DATASET ==========
    num_customers = num_orders // 3  # About 33% repeat customers
    customer_ids = [f"CUST_{i:06d}" for i in range(1, num_customers + 1)]

    brazilian_states = ['SP', 'RJ', 'MG', 'RS', 'PR', 'BA', 'SC', 'PE', 'CE', 'GO']
    brazilian_cities = {
        'SP': ['Sao Paulo', 'Campinas', 'Santos', 'Sorocaba'],
        'RJ': ['Rio de Janeiro', 'Niteroi', 'Petropolis'],
        'MG': ['Belo Horizonte', 'Uberlandia', 'Contagem'],
        'RS': ['Porto Alegre', 'Caxias do Sul', 'Pelotas'],
        'PR': ['Curitiba', 'Londrina', 'Maringa'],
        'BA': ['Salvador', 'Feira de Santana'],
        'SC': ['Florianopolis', 'Joinville', 'Blumenau'],
        'PE': ['Recife', 'Olinda'],
        'CE': ['Fortaleza', 'Caucaia'],
        'GO': ['Goiania', 'Aparecida de Goiania']
    }

    customers_data = {
        'customer_id': customer_ids,
        'customer_unique_id': customer_ids,  # Simplified
        'customer_zip_code_prefix': [f"{random.randint(10000, 99999)}" for _ in range(num_customers)],
        'customer_city': [random.choice(brazilian_cities[state]) for state in
                         [random.choice(brazilian_states) for _ in range(num_customers)]],
        'customer_state': [random.choice(brazilian_states) for _ in range(num_customers)]
    }
    customers_df = pd.DataFrame(customers_data)
    customers_df.to_csv(os.path.join(output_dir, 'olist_customers_dataset.csv'), index=False)
    print(f"  Created customers: {len(customers_df):,}")

    # ========== ORDERS DATASET ==========
    order_timestamps = [
        start_date + timedelta(days=random.randint(0, 364),
                               hours=random.randint(0, 23),
                               minutes=random.randint(0, 59))
        for _ in range(num_orders)
    ]

    orders_data = {
        'order_id': order_ids,
        'customer_id': [random.choice(customer_ids) for _ in range(num_orders)],
        'order_status': np.random.choice(
            ['delivered', 'delivered', 'delivered', 'delivered',
             'shipped', 'processing', 'cancelled'],
            size=num_orders
        ),
        'order_purchase_timestamp': order_timestamps,
        'order_approved_at': [ts + timedelta(hours=random.randint(1, 24))
                              for ts in order_timestamps],
        'order_delivered_carrier_date': [ts + timedelta(days=random.randint(1, 3))
                                         for ts in order_timestamps],
        'order_delivered_customer_date': [ts + timedelta(days=random.randint(5, 25))
                                          for ts in order_timestamps],
        'order_estimated_delivery_date': [ts + timedelta(days=random.randint(10, 20))
                                          for ts in order_timestamps]
    }
    orders_df = pd.DataFrame(orders_data)
    orders_df.to_csv(os.path.join(output_dir, 'olist_orders_dataset.csv'), index=False)
    print(f"  Created orders: {len(orders_df):,}")

    # ========== PRODUCTS DATASET ==========
    product_categories = [
        'electronics', 'home_furniture', 'bed_bath_table', 'sports',
        'toys', 'fashion', 'beauty', 'phones', 'computers', 'garden',
        'food', 'books', 'baby', 'health', 'auto'
    ]

    num_products = 500
    product_ids = [f"PROD_{i:06d}" for i in range(1, num_products + 1)]

    products_data = {
        'product_id': product_ids,
        'product_category_name': [random.choice(product_categories) for _ in range(num_products)],
        'product_name_lgt': [f"Product {i}" for i in range(1, num_products + 1)],
        'product_weight_lg': np.round(np.random.uniform(0.1, 20, num_products), 2),
        'product_length_cm': np.round(np.random.uniform(5, 50, num_products), 1),
        'product_height_cm': np.round(np.random.uniform(2, 30, num_products), 1),
        'product_width_cm': np.round(np.random.uniform(5, 40, num_products), 1)
    }
    products_df = pd.DataFrame(products_data)
    products_df.to_csv(os.path.join(output_dir, 'olist_products_dataset.csv'), index=False)
    print(f"  Created products: {len(products_df):,}")

    # ========== CATEGORY TRANSLATION ==========
    category_translation = {
        'product_category_name': product_categories,
        'product_category_name_english': product_categories  # Same for simplicity
    }
    translation_df = pd.DataFrame(category_translation)
    translation_df.to_csv(os.path.join(output_dir, 'olist_products_category_name_translation.csv'),
                          index=False)
    print(f"  Created category translation")

    # ========== SELLERS DATASET ==========
    num_sellers = 50
    seller_ids = [f"SELL_{i:06d}" for i in range(1, num_sellers + 1)]

    sellers_data = {
        'seller_id': seller_ids,
        'seller_zip_code_prefix': [f"{random.randint(10000, 99999)}" for _ in range(num_sellers)],
        'seller_city': [random.choice(['Sao Paulo', 'Rio de Janeiro', 'Curitiba', 'Belo Horizonte'])
                        for _ in range(num_sellers)],
        'seller_state': [random.choice(brazilian_states) for _ in range(num_sellers)]
    }
    sellers_df = pd.DataFrame(sellers_data)
    sellers_df.to_csv(os.path.join(output_dir, 'olist_sellers_dataset.csv'), index=False)
    print(f"  Created sellers: {len(sellers_df):,}")

    # ========== ORDER ITEMS DATASET ==========
    # Each order can have 1-5 items
    order_items_list = []
    for order_id in order_ids:
        num_items = random.randint(1, 5)
        for item_num in range(1, num_items + 1):
            order_items_list.append({
                'order_id': order_id,
                'order_item_id': item_num,
                'product_id': random.choice(product_ids),
                'seller_id': random.choice(seller_ids),
                'shipping_limit_date': start_date + timedelta(days=random.randint(1, 365)),
                'price': round(random.uniform(10, 500), 2),
                'freight_value': round(random.uniform(5, 50), 2)
            })

    order_items_df = pd.DataFrame(order_items_list)
    order_items_df.to_csv(os.path.join(output_dir, 'olist_order_items_dataset.csv'), index=False)
    print(f"  Created order items: {len(order_items_df):,}")

    # ========== ORDER PAYMENTS DATASET ==========
    payment_types = ['credit_card', 'credit_card', 'credit_card',
                     'boleto', 'debit_card', 'voucher']

    payments_list = []
    for order_id in order_ids:
        num_installments = random.choices(
            [1, 2, 3, 4, 5, 6, 10, 12],
            weights=[30, 15, 15, 10, 10, 8, 7, 5]
        )[0]

        # Get total order value
        order_total = order_items_df[
            order_items_df['order_id'] == order_id
        ]['price'].sum()

        payments_list.append({
            'order_id': order_id,
            'payment_sequential': 1,
            'payment_type': random.choice(payment_types),
            'payment_installments': num_installments,
            'payment_value': round(order_total, 2)
        })

    payments_df = pd.DataFrame(payments_list)
    payments_df.to_csv(os.path.join(output_dir, 'olist_order_payments_dataset.csv'), index=False)
    print(f"  Created payments: {len(payments_df):,}")

    # Add review scores dataset
    review_scores = {
        'order_id': order_ids,
        'review_score': np.random.choice([1, 2, 3, 4, 5], size=num_orders,
                                          p=[0.05, 0.05, 0.15, 0.35, 0.40]),
        'review_comment_title': [None] * num_orders,
        'review_comment_body': [None] * num_orders,
        'review_creation_date': order_timestamps,
        'review_answer_timestamp': [ts + timedelta(days=random.randint(1, 5))
                                    for ts in order_timestamps]
    }
    reviews_df = pd.DataFrame(review_scores)
    reviews_df.to_csv(os.path.join(output_dir, 'olist_order_reviews_dataset.csv'), index=False)
    print(f"  Created reviews: {len(reviews_df):,}")

    print(f"\nSample data generation complete!")
    print(f"Files saved to: {output_dir}")


if __name__ == "__main__":
    # Generate sample data in the data directory
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    generate_sample_data(data_dir, num_orders=5000)
