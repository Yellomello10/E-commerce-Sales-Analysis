"""
Advanced Insights Module

Implements advanced analytics including:
- Cohort Analysis
- Customer Segmentation (RFM)
- Customer Lifetime Value Prediction
- Sales Forecasting
- Market Basket Analysis
- Churn Prediction Indicators
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List
from datetime import datetime, timedelta


def perform_cohort_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform cohort analysis to track customer retention over time.

    Args:
        df: DataFrame with customer_id and order_purchase_timestamp

    Returns:
        Dictionary containing cohort data and retention matrix
    """
    result = {
        'cohort_data': None,
        'retention_matrix': None,
        'cohort_sizes': None
    }

    if 'customer_id' not in df.columns or 'order_purchase_timestamp' not in df.columns:
        return result

    df = df.copy()
    df = df.dropna(subset=['order_purchase_timestamp', 'customer_id'])

    if len(df) == 0:
        return result

    # Assign cohort based on first purchase month
    df['cohort'] = df.groupby('customer_id')['order_purchase_timestamp'].transform('min').dt.to_period('M')

    # Calculate period number for each order
    df['order_period'] = df['order_purchase_timestamp'].dt.to_period('M')
    df['period_number'] = (df['order_period'].astype(int) - df['cohort'].astype(int))

    # Create cohort table
    cohort_table = pd.crosstab(df['cohort'], df['period_number'])

    # Calculate cohort sizes (first period)
    cohort_sizes = cohort_table.iloc[:, 0]

    # Calculate retention rates
    retention_matrix = cohort_table.divide(cohort_sizes, axis=0) * 100

    result['cohort_data'] = cohort_table
    result['retention_matrix'] = retention_matrix
    result['cohort_sizes'] = cohort_sizes

    return result


def perform_rfm_segmentation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform RFM (Recency, Frequency, Monetary) customer segmentation.

    Args:
        df: DataFrame with customer_id, order_purchase_timestamp, and price

    Returns:
        DataFrame with RFM scores and segments for each customer
    """
    if 'customer_id' not in df.columns:
        return pd.DataFrame()

    if 'order_purchase_timestamp' not in df.columns or 'price' not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df = df.dropna(subset=['customer_id', 'order_purchase_timestamp', 'price'])

    # Reference date for recency calculation
    reference_date = df['order_purchase_timestamp'].max() + timedelta(days=1)

    # Calculate RFM metrics
    rfm = df.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (reference_date - x.max()).days,
        'order_id': 'nunique',
        'price': 'sum'
    }).reset_index()

    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']

    # Assign RFM scores (1-5 scale)
    rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')

    # Convert scores to numeric
    rfm['r_score'] = rfm['r_score'].astype(int)
    rfm['f_score'] = rfm['f_score'].astype(int)
    rfm['m_score'] = rfm['m_score'].astype(int)

    # Calculate combined RFM score
    rfm['rfm_score'] = rfm['r_score'] * 100 + rfm['f_score'] * 10 + rfm['m_score']

    # Assign customer segments
    def assign_segment(row):
        r, f, m = row['r_score'], row['f_score'], row['m_score']

        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3 and m >= 3:
            return 'Loyal Customers'
        elif r >= 4 and f <= 2:
            return 'New Customers'
        elif r >= 3 and f >= 3 and m <= 2:
            return 'Potential Loyalists'
        elif r <= 2 and f >= 3:
            return 'At Risk'
        elif r <= 2 and f <= 2 and m >= 3:
            return 'Hibernating'
        elif r <= 2 and f <= 2:
            return 'Lost'
        else:
            return 'Regular'

    rfm['segment'] = rfm.apply(assign_segment, axis=1)

    return rfm


def calculate_customer_lifetime_value(df: pd.DataFrame, months_ahead: int = 12) -> pd.DataFrame:
    """
    Calculate and predict Customer Lifetime Value (CLV).

    Args:
        df: DataFrame with customer_id, order_purchase_timestamp, and price
        months_ahead: Number of months to predict CLV for

    Returns:
        DataFrame with CLV predictions per customer
    """
    if 'customer_id' not in df.columns or 'price' not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df = df.dropna(subset=['customer_id', 'order_purchase_timestamp', 'price'])

    # Calculate historical metrics per customer
    customer_metrics = df.groupby('customer_id').agg({
        'order_purchase_timestamp': ['min', 'max', 'count'],
        'price': ['sum', 'mean']
    })
    customer_metrics.columns = ['first_purchase', 'last_purchase', 'num_orders', 'total_spent', 'avg_order_value']
    customer_metrics = customer_metrics.reset_index()

    # Calculate customer age in months
    customer_metrics['customer_age_months'] = (
        (customer_metrics['last_purchase'] - customer_metrics['first_purchase']).dt.days / 30
    ).clip(lower=1)

    # Calculate monthly spend rate
    customer_metrics['monthly_spend'] = customer_metrics['total_spent'] / customer_metrics['customer_age_months']

    # Predict CLV
    customer_metrics['predicted_clv'] = customer_metrics['monthly_spend'] * months_ahead

    # Apply discount rate (assuming 10% annual discount rate)
    discount_rate = 0.10 / 12  # Monthly discount rate
    customer_metrics['discounted_clv'] = customer_metrics['predicted_clv'] / (1 + discount_rate) ** months_ahead

    return customer_metrics


def forecast_sales(df: pd.DataFrame, periods: int = 3) -> pd.DataFrame:
    """
    Simple sales forecasting using moving average and trend analysis.

    Args:
        df: DataFrame with order_purchase_timestamp and price
        periods: Number of periods (months) to forecast

    Returns:
        DataFrame with historical and forecasted sales
    """
    if 'order_purchase_timestamp' not in df.columns or 'price' not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df = df.dropna(subset=['order_purchase_timestamp', 'price'])

    # Aggregate monthly sales
    monthly_sales = df.groupby(
        df['order_purchase_timestamp'].dt.to_period('M')
    )['price'].sum().reset_index()
    monthly_sales.columns = ['month', 'sales']

    if len(monthly_sales) < 3:
        return monthly_sales

    # Calculate moving average (3-month)
    monthly_sales['ma_3'] = monthly_sales['sales'].rolling(window=3, min_periods=1).mean()

    # Calculate growth rate
    monthly_sales['growth_rate'] = monthly_sales['sales'].pct_change()
    avg_growth_rate = monthly_sales['growth_rate'].mean()

    # Generate forecast
    last_month = monthly_sales['month'].max()
    last_sales = monthly_sales['sales'].iloc[-1]

    forecast_data = []
    for i in range(1, periods + 1):
        forecast_month = last_month + i
        forecast_value = last_sales * (1 + avg_growth_rate) ** i if pd.notna(avg_growth_rate) else last_sales
        forecast_data.append({
            'month': forecast_month,
            'sales': forecast_value,
            'ma_3': np.nan,
            'growth_rate': avg_growth_rate if pd.notna(avg_growth_rate) else 0,
            'is_forecast': True
        })

    monthly_sales['is_forecast'] = False
    forecast_df = pd.DataFrame(forecast_data)

    return pd.concat([monthly_sales, forecast_df], ignore_index=True)


def analyze_product_affinity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze product affinity (which products are frequently bought together).

    Args:
        df: DataFrame with order_id and product_id

    Returns:
        DataFrame with product pairs and their co-occurrence count
    """
    if 'order_id' not in df.columns or 'product_id' not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df = df.dropna(subset=['order_id', 'product_id'])

    # Get products per order
    order_products = df.groupby('order_id')['product_id'].apply(list).reset_index()
    order_products.columns = ['order_id', 'products']

    # Filter orders with multiple products
    order_products = order_products[order_products['products'].apply(len) > 1]

    if len(order_products) == 0:
        return pd.DataFrame(columns=['product_1', 'product_2', 'co_occurrence'])

    # Count product pair co-occurrences
    from itertools import combinations

    pair_counts = {}
    for products in order_products['products']:
        for pair in combinations(sorted(set(products)), 2):
            if pair not in pair_counts:
                pair_counts[pair] = 0
            pair_counts[pair] += 1

    # Convert to DataFrame
    affinity_df = pd.DataFrame([
        {'product_1': pair[0], 'product_2': pair[1], 'co_occurrence': count}
        for pair, count in pair_counts.items()
    ])

    # Sort by co-occurrence
    affinity_df = affinity_df.sort_values('co_occurrence', ascending=False)

    return affinity_df


def calculate_churn_risk(df: pd.DataFrame, days_threshold: int = 90) -> pd.DataFrame:
    """
    Calculate churn risk indicators for customers.

    Args:
        df: DataFrame with customer_id and order_purchase_timestamp
        days_threshold: Days since last purchase to consider as churned

    Returns:
        DataFrame with churn risk assessment per customer
    """
    if 'customer_id' not in df.columns or 'order_purchase_timestamp' not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df = df.dropna(subset=['customer_id', 'order_purchase_timestamp'])

    # Reference date
    reference_date = df['order_purchase_timestamp'].max()

    # Calculate metrics per customer
    customer_activity = df.groupby('customer_id').agg({
        'order_purchase_timestamp': ['max', 'min', 'count'],
        'order_id': 'nunique'
    })
    customer_activity.columns = ['last_purchase', 'first_purchase', 'total_orders', 'unique_orders']
    customer_activity = customer_activity.reset_index()

    # Days since last purchase
    customer_activity['days_since_purchase'] = (reference_date - customer_activity['last_purchase']).dt.days

    # Purchase frequency (avg days between purchases)
    customer_activity['customer_tenure_days'] = (
        customer_activity['last_purchase'] - customer_activity['first_purchase']
    ).dt.days

    customer_activity['avg_purchase_interval'] = np.where(
        customer_activity['total_orders'] > 1,
        customer_activity['customer_tenure_days'] / (customer_activity['total_orders'] - 1),
        customer_activity['customer_tenure_days']
    )

    # Churn risk score
    def calculate_risk_score(row):
        days_since = row['days_since_purchase']
        avg_interval = row['avg_purchase_interval']

        if days_since > days_threshold:
            return 'High'
        elif days_since > avg_interval * 2:
            return 'Medium'
        elif days_since > avg_interval:
            return 'Low'
        else:
            return 'Very Low'

    customer_activity['churn_risk'] = customer_activity.apply(calculate_risk_score, axis=1)

    return customer_activity


def analyze_customer_journey(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze customer journey patterns.

    Args:
        df: DataFrame with customer_id, order_purchase_timestamp, and price

    Returns:
        Dictionary with journey analysis metrics
    """
    result = {
        'avg_time_to_second_purchase': None,
        'purchase_frequency_distribution': None,
        'customer_lifecycle_stages': None
    }

    if 'customer_id' not in df.columns or 'order_purchase_timestamp' not in df.columns:
        return result

    df = df.copy()
    df = df.dropna(subset=['customer_id', 'order_purchase_timestamp'])

    # Calculate time between purchases
    df_sorted = df.sort_values(['customer_id', 'order_purchase_timestamp'])

    # Time to second purchase
    first_purchase = df_sorted.groupby('customer_id')['order_purchase_timestamp'].first()
    second_purchase = df_sorted.groupby('customer_id')['order_purchase_timestamp'].nth(1)

    time_to_second = (second_purchase - first_purchase).dt.days
    result['avg_time_to_second_purchase'] = time_to_second.dropna().mean()

    # Purchase frequency distribution
    purchase_counts = df.groupby('customer_id')['order_id'].nunique()
    result['purchase_frequency_distribution'] = purchase_counts.value_counts().sort_index()

    # Customer lifecycle stages
    reference_date = df['order_purchase_timestamp'].max()
    customer_recency = df.groupby('customer_id')['order_purchase_timestamp'].max()
    days_since = (reference_date - customer_recency).dt.days

    def assign_lifecycle(days):
        if days <= 30:
            return 'Active'
        elif days <= 60:
            return 'Warm'
        elif days <= 90:
            return 'Cooling'
        else:
            return 'Inactive'

    lifecycle = days_since.apply(assign_lifecycle)
    result['customer_lifecycle_stages'] = lifecycle.value_counts()

    return result


def generate_advanced_insights_report(df: pd.DataFrame) -> str:
    """
    Generate comprehensive advanced insights report.

    Args:
        df: Merged DataFrame

    Returns:
        Formatted string report
    """
    lines = []
    lines.append("=" * 70)
    lines.append("              ADVANCED ANALYTICS INSIGHTS REPORT")
    lines.append("=" * 70)
    lines.append("")

    # RFM Segmentation
    lines.append("CUSTOMER SEGMENTATION (RFM Analysis)")
    lines.append("-" * 50)
    rfm = perform_rfm_segmentation(df)
    if not rfm.empty:
        segment_summary = rfm['segment'].value_counts()
        for segment, count in segment_summary.items():
            pct = count / len(rfm) * 100
            lines.append(f"  {segment}: {count:,} ({pct:.1f}%)")

        # Top customers by CLV
        lines.append("")
        lines.append("  Top 5 Customers by Value:")
        top_customers = rfm.nlargest(5, 'rfm_score')[['customer_id', 'segment', 'rfm_score']]
        for _, row in top_customers.iterrows():
            lines.append(f"    - {row['customer_id']}: {row['segment']} (Score: {row['rfm_score']})")
    else:
        lines.append("  Insufficient data for RFM analysis")
    lines.append("")

    # Churn Risk
    lines.append("CHURN RISK ANALYSIS")
    lines.append("-" * 50)
    churn = calculate_churn_risk(df)
    if not churn.empty:
        churn_summary = churn['churn_risk'].value_counts()
        for risk, count in churn_summary.items():
            pct = count / len(churn) * 100
            lines.append(f"  {risk} Risk: {count:,} ({pct:.1f}%)")
    else:
        lines.append("  Insufficient data for churn analysis")
    lines.append("")

    # Customer Journey
    lines.append("CUSTOMER JOURNEY INSIGHTS")
    lines.append("-" * 50)
    journey = analyze_customer_journey(df)
    if journey['avg_time_to_second_purchase']:
        lines.append(f"  Avg Time to Second Purchase: {journey['avg_time_to_second_purchase']:.1f} days")
    if journey['customer_lifecycle_stages'] is not None:
        lines.append("  Customer Lifecycle Distribution:")
        for stage, count in journey['customer_lifecycle_stages'].items():
            lines.append(f"    - {stage}: {count:,} customers")
    lines.append("")

    # Product Affinity
    lines.append("PRODUCT AFFINITY ANALYSIS")
    lines.append("-" * 50)
    affinity = analyze_product_affinity(df)
    if not affinity.empty:
        lines.append("  Top 5 Product Pairs Bought Together:")
        for _, row in affinity.head(5).iterrows():
            lines.append(f"    - Product {row['product_1']} + Product {row['product_2']}: {row['co_occurrence']} orders")
    else:
        lines.append("  Insufficient data for affinity analysis (need orders with multiple products)")
    lines.append("")

    # Sales Forecast
    lines.append("SALES FORECAST (Next 3 Months)")
    lines.append("-" * 50)
    forecast = forecast_sales(df, periods=3)
    forecast_data = forecast[forecast['is_forecast'] == True]
    if not forecast_data.empty:
        for _, row in forecast_data.iterrows():
            lines.append(f"  {row['month']}: ${row['sales']:,.2f} (projected)")
    else:
        lines.append("  Insufficient data for forecasting")
    lines.append("")

    # Recommendations
    lines.append("STRATEGIC RECOMMENDATIONS")
    lines.append("-" * 50)

    if not rfm.empty:
        lost_customers = len(rfm[rfm['segment'] == 'Lost'])
        at_risk = len(rfm[rfm['segment'] == 'At Risk'])

        if lost_customers > 0:
            lines.append(f"  1. Re-engagement Campaign: Target {lost_customers} 'Lost' customers with win-back offers")

        if at_risk > 0:
            lines.append(f"  2. Retention Focus: {at_risk} 'At Risk' customers need immediate attention")

        champions = len(rfm[rfm['segment'] == 'Champions'])
        if champions > 0:
            lines.append(f"  3. Loyalty Program: Engage {champions} 'Champions' with exclusive rewards")

    if not churn.empty:
        high_risk = len(churn[churn['churn_risk'] == 'High'])
        if high_risk > 0:
            lines.append(f"  4. Churn Prevention: {high_risk} high-risk customers need proactive outreach")

    if not affinity.empty:
        lines.append("  5. Cross-selling: Bundle top product pairs to increase average order value")

    lines.append("")
    lines.append("=" * 70)
    lines.append("End of Advanced Analytics Report")
    lines.append("=" * 70)

    return "\n".join(lines)
