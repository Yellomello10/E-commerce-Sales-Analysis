"""
KPI Dashboard Module

Calculates and displays key performance indicators for e-commerce analytics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from datetime import datetime


def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate comprehensive KPIs from the merged dataset.

    Args:
        df: Merged DataFrame with all e-commerce data

    Returns:
        Dictionary containing all KPI metrics
    """
    kpis = {}

    # ========== REVENUE KPIS ==========
    kpis['revenue'] = calculate_revenue_kpis(df)

    # ========== CUSTOMER KPIS ==========
    kpis['customers'] = calculate_customer_kpis(df)

    # ========== PRODUCT KPIS ==========
    kpis['products'] = calculate_product_kpis(df)

    # ========== DELIVERY KPIS ==========
    kpis['delivery'] = calculate_delivery_kpis(df)

    # ========== PAYMENT KPIS ==========
    kpis['payments'] = calculate_payment_kpis(df)

    # ========== ORDER KPIS ==========
    kpis['orders'] = calculate_order_kpis(df)

    return kpis


def calculate_revenue_kpis(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate revenue-related KPIs."""
    kpis = {}

    if 'price' not in df.columns:
        return {
            'total_revenue': 0,
            'avg_daily_revenue': 0,
            'revenue_growth_rate': 0,
            'revenue_per_customer': 0,
            'revenue_per_order': 0
        }

    # Total Revenue
    kpis['total_revenue'] = df['price'].sum()

    # Daily Revenue
    if 'order_purchase_timestamp' in df.columns:
        df_valid = df.dropna(subset=['order_purchase_timestamp'])
        daily_revenue = df_valid.groupby(
            df_valid['order_purchase_timestamp'].dt.date
        )['price'].sum()
        kpis['avg_daily_revenue'] = daily_revenue.mean()
        kpis['max_daily_revenue'] = daily_revenue.max()
        kpis['min_daily_revenue'] = daily_revenue.min()

        # Revenue Growth Rate (comparing last month to previous month)
        monthly_revenue = df_valid.groupby(
            df_valid['order_purchase_timestamp'].dt.to_period('M')
        )['price'].sum()

        if len(monthly_revenue) >= 2:
            last_month = monthly_revenue.iloc[-1]
            prev_month = monthly_revenue.iloc[-2]
            kpis['revenue_growth_rate'] = ((last_month - prev_month) / prev_month * 100) if prev_month > 0 else 0
        else:
            kpis['revenue_growth_rate'] = 0
    else:
        kpis['avg_daily_revenue'] = 0
        kpis['max_daily_revenue'] = 0
        kpis['min_daily_revenue'] = 0
        kpis['revenue_growth_rate'] = 0

    # Revenue Per Customer
    if 'customer_id' in df.columns:
        customer_revenue = df.groupby('customer_id')['price'].sum()
        kpis['revenue_per_customer'] = customer_revenue.mean()
    else:
        kpis['revenue_per_customer'] = 0

    # Revenue Per Order
    if 'order_id' in df.columns:
        order_revenue = df.groupby('order_id')['price'].sum()
        kpis['revenue_per_order'] = order_revenue.mean()
    else:
        kpis['revenue_per_order'] = 0

    # Average Ticket Value
    kpis['avg_ticket_value'] = kpis['revenue_per_order']

    return kpis


def calculate_customer_kpis(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate customer-related KPIs."""
    kpis = {}

    if 'customer_id' not in df.columns:
        return {
            'total_customers': 0,
            'new_customers': 0,
            'repeat_customer_rate': 0,
            'customer_acquisition_cost': 0,
            'avg_orders_per_customer': 0
        }

    # Total Unique Customers
    kpis['total_customers'] = df['customer_id'].nunique()

    # Orders per Customer
    orders_per_customer = df.groupby('customer_id')['order_id'].nunique()
    kpis['avg_orders_per_customer'] = orders_per_customer.mean()
    kpis['max_orders_per_customer'] = orders_per_customer.max()

    # Repeat Customers
    repeat_customers = (orders_per_customer > 1).sum()
    kpis['repeat_customers'] = repeat_customers
    kpis['new_customers'] = (orders_per_customer == 1).sum()
    kpis['repeat_customer_rate'] = (repeat_customers / kpis['total_customers'] * 100) if kpis['total_customers'] > 0 else 0

    # Customer Lifetime Value (CLV) - Simplified
    if 'price' in df.columns:
        customer_lifetime_value = df.groupby('customer_id')['price'].sum()
        kpis['avg_customer_lifetime_value'] = customer_lifetime_value.mean()
        kpis['max_customer_lifetime_value'] = customer_lifetime_value.max()
    else:
        kpis['avg_customer_lifetime_value'] = 0
        kpis['max_customer_lifetime_value'] = 0

    return kpis


def calculate_product_kpis(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate product-related KPIs."""
    kpis = {}

    if 'product_id' not in df.columns:
        return {
            'total_products_sold': 0,
            'unique_products_sold': 0,
            'avg_items_per_order': 0,
            'return_rate': 0
        }

    # Total Items Sold
    kpis['total_items_sold'] = len(df)

    # Unique Products Sold
    kpis['unique_products_sold'] = df['product_id'].nunique()

    # Items Per Order
    if 'order_id' in df.columns:
        items_per_order = df.groupby('order_id').size()
        kpis['avg_items_per_order'] = items_per_order.mean()
        kpis['max_items_per_order'] = items_per_order.max()
    else:
        kpis['avg_items_per_order'] = 0
        kpis['max_items_per_order'] = 0

    # Product Concentration (Top 10 products % of total revenue)
    if 'price' in df.columns:
        product_revenue = df.groupby('product_id')['price'].sum()
        top_10_revenue = product_revenue.nlargest(10).sum()
        total_revenue = product_revenue.sum()
        kpis['top_10_product_concentration'] = (top_10_revenue / total_revenue * 100) if total_revenue > 0 else 0
    else:
        kpis['top_10_product_concentration'] = 0

    return kpis


def calculate_delivery_kpis(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate delivery-related KPIs."""
    kpis = {}

    # Default values
    default_kpis = {
        'avg_delivery_time_days': 0,
        'on_time_delivery_rate': 0,
        'delay_rate': 0,
        'avg_freight_value': 0,
        'freight_to_revenue_ratio': 0
    }

    if 'order_purchase_timestamp' not in df.columns or 'order_delivered_customer_date' not in df.columns:
        return default_kpis

    df_valid = df.dropna(subset=['order_purchase_timestamp', 'order_delivered_customer_date'])

    if len(df_valid) == 0:
        return default_kpis

    # Calculate Delivery Time
    df_valid = df_valid.copy()
    df_valid['delivery_time'] = (
        df_valid['order_delivered_customer_date'] - df_valid['order_purchase_timestamp']
    ).dt.days

    valid_delivery = df_valid[(df_valid['delivery_time'] >= 0) & (df_valid['delivery_time'] <= 60)]

    if len(valid_delivery) > 0:
        kpis['avg_delivery_time_days'] = valid_delivery['delivery_time'].mean()
        kpis['median_delivery_time_days'] = valid_delivery['delivery_time'].median()
        kpis['std_delivery_time_days'] = valid_delivery['delivery_time'].std()
    else:
        kpis['avg_delivery_time_days'] = 0
        kpis['median_delivery_time_days'] = 0
        kpis['std_delivery_time_days'] = 0

    # On-Time Delivery Rate
    if 'order_estimated_delivery_date' in df_valid.columns:
        df_valid = df_valid.dropna(subset=['order_estimated_delivery_date'])
        on_time = (df_valid['order_delivered_customer_date'] <= df_valid['order_estimated_delivery_date']).sum()
        total_delivered = df_valid['order_delivered_customer_date'].notna().sum()
        kpis['on_time_delivery_rate'] = (on_time / total_delivered * 100) if total_delivered > 0 else 0
        kpis['delay_rate'] = 100 - kpis['on_time_delivery_rate']
    else:
        kpis['on_time_delivery_rate'] = 0
        kpis['delay_rate'] = 0

    # Freight Value
    if 'freight_value' in df.columns:
        kpis['avg_freight_value'] = df['freight_value'].mean()
        if 'price' in df.columns and df['price'].sum() > 0:
            kpis['freight_to_revenue_ratio'] = (df['freight_value'].sum() / df['price'].sum() * 100)
        else:
            kpis['freight_to_revenue_ratio'] = 0
    else:
        kpis['avg_freight_value'] = 0
        kpis['freight_to_revenue_ratio'] = 0

    return kpis


def calculate_payment_kpis(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate payment-related KPIs."""
    kpis = {}

    if 'payment_type' not in df.columns:
        return {
            'credit_card_usage_rate': 0,
            'avg_installments': 0,
            'installment_usage_rate': 0,
            'avg_payment_value': 0
        }

    # Payment Type Distribution
    payment_counts = df['payment_type'].value_counts()
    total_payments = payment_counts.sum()

    if 'credit_card' in payment_counts.index:
        kpis['credit_card_usage_rate'] = (payment_counts['credit_card'] / total_payments * 100)
    else:
        kpis['credit_card_usage_rate'] = 0

    # Installments
    if 'payment_installments' in df.columns:
        kpis['avg_installments'] = df['payment_installments'].mean()
        kpis['max_installments'] = df['payment_installments'].max()
        installment_orders = (df['payment_installments'] > 1).sum()
        kpis['installment_usage_rate'] = (installment_orders / len(df) * 100) if len(df) > 0 else 0
    else:
        kpis['avg_installments'] = 0
        kpis['max_installments'] = 0
        kpis['installment_usage_rate'] = 0

    # Payment Value
    if 'payment_value' in df.columns:
        kpis['avg_payment_value'] = df['payment_value'].mean()
        kpis['total_payment_value'] = df['payment_value'].sum()
    else:
        kpis['avg_payment_value'] = 0
        kpis['total_payment_value'] = 0

    return kpis


def calculate_order_kpis(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate order-related KPIs."""
    kpis = {}

    if 'order_id' not in df.columns:
        return {
            'total_orders': 0,
            'avg_order_frequency': 0,
            'cancellation_rate': 0,
            'orders_per_day': 0
        }

    # Total Orders
    kpis['total_orders'] = df['order_id'].nunique()

    # Order Status Analysis
    if 'order_status' in df.columns:
        status_counts = df['order_status'].value_counts()
        total = status_counts.sum()

        if 'delivered' in status_counts.index:
            kpis['delivery_completion_rate'] = (status_counts['delivered'] / total * 100)
        else:
            kpis['delivery_completion_rate'] = 0

        if 'cancelled' in status_counts.index:
            kpis['cancellation_rate'] = (status_counts['cancelled'] / total * 100)
        else:
            kpis['cancellation_rate'] = 0
    else:
        kpis['delivery_completion_rate'] = 0
        kpis['cancellation_rate'] = 0

    # Orders Per Day
    if 'order_purchase_timestamp' in df.columns:
        df_valid = df.dropna(subset=['order_purchase_timestamp'])
        daily_orders = df_valid.groupby(
            df_valid['order_purchase_timestamp'].dt.date
        )['order_id'].nunique()
        kpis['orders_per_day'] = daily_orders.mean()
        kpis['peak_order_day'] = str(daily_orders.idxmax()) if len(daily_orders) > 0 else 'N/A'
    else:
        kpis['orders_per_day'] = 0
        kpis['peak_order_day'] = 'N/A'

    # Review Score
    if 'review_score' in df.columns:
        kpis['avg_review_score'] = df['review_score'].mean()
        kpis['positive_review_rate'] = (df['review_score'] >= 4).sum() / len(df) * 100
    else:
        kpis['avg_review_score'] = 0
        kpis['positive_review_rate'] = 0

    return kpis


def generate_kpi_summary(kpis: Dict[str, Any]) -> str:
    """
    Generate a formatted KPI summary report.

    Args:
        kpis: Dictionary of KPIs from calculate_kpis()

    Returns:
        Formatted string with KPI summary
    """
    lines = []
    lines.append("=" * 70)
    lines.append("                    KPI DASHBOARD SUMMARY")
    lines.append("=" * 70)
    lines.append("")

    # Revenue KPIs
    rev = kpis.get('revenue', {})
    lines.append("REVENUE METRICS")
    lines.append("-" * 40)
    lines.append(f"  Total Revenue:           ${rev.get('total_revenue', 0):>15,.2f}")
    lines.append(f"  Avg Daily Revenue:       ${rev.get('avg_daily_revenue', 0):>15,.2f}")
    lines.append(f"  Revenue Growth Rate:     {rev.get('revenue_growth_rate', 0):>15.1f}%")
    lines.append(f"  Revenue Per Customer:    ${rev.get('revenue_per_customer', 0):>15,.2f}")
    lines.append(f"  Avg Ticket Value:        ${rev.get('avg_ticket_value', 0):>15,.2f}")
    lines.append("")

    # Customer KPIs
    cust = kpis.get('customers', {})
    lines.append("CUSTOMER METRICS")
    lines.append("-" * 40)
    lines.append(f"  Total Customers:         {cust.get('total_customers', 0):>15,}")
    lines.append(f"  New Customers:           {cust.get('new_customers', 0):>15,}")
    lines.append(f"  Repeat Customers:        {cust.get('repeat_customers', 0):>15,}")
    lines.append(f"  Repeat Customer Rate:    {cust.get('repeat_customer_rate', 0):>15.1f}%")
    lines.append(f"  Avg Orders Per Customer: {cust.get('avg_orders_per_customer', 0):>15.2f}")
    lines.append(f"  Avg Customer LTV:        ${cust.get('avg_customer_lifetime_value', 0):>15,.2f}")
    lines.append("")

    # Product KPIs
    prod = kpis.get('products', {})
    lines.append("PRODUCT METRICS")
    lines.append("-" * 40)
    lines.append(f"  Total Items Sold:        {prod.get('total_items_sold', 0):>15,}")
    lines.append(f"  Unique Products:         {prod.get('unique_products_sold', 0):>15,}")
    lines.append(f"  Avg Items Per Order:     {prod.get('avg_items_per_order', 0):>15.2f}")
    lines.append(f"  Top 10 Concentration:    {prod.get('top_10_product_concentration', 0):>15.1f}%")
    lines.append("")

    # Delivery KPIs
    del_kpis = kpis.get('delivery', {})
    lines.append("DELIVERY METRICS")
    lines.append("-" * 40)
    lines.append(f"  Avg Delivery Time:       {del_kpis.get('avg_delivery_time_days', 0):>15.1f} days")
    lines.append(f"  On-Time Delivery Rate:   {del_kpis.get('on_time_delivery_rate', 0):>15.1f}%")
    lines.append(f"  Delay Rate:              {del_kpis.get('delay_rate', 0):>15.1f}%")
    lines.append(f"  Avg Freight Value:       ${del_kpis.get('avg_freight_value', 0):>15,.2f}")
    lines.append(f"  Freight/Revenue Ratio:   {del_kpis.get('freight_to_revenue_ratio', 0):>15.1f}%")
    lines.append("")

    # Payment KPIs
    pay = kpis.get('payments', {})
    lines.append("PAYMENT METRICS")
    lines.append("-" * 40)
    lines.append(f"  Credit Card Usage:       {pay.get('credit_card_usage_rate', 0):>15.1f}%")
    lines.append(f"  Avg Installments:        {pay.get('avg_installments', 0):>15.1f}x")
    lines.append(f"  Installment Usage Rate:  {pay.get('installment_usage_rate', 0):>15.1f}%")
    lines.append(f"  Avg Payment Value:       ${pay.get('avg_payment_value', 0):>15,.2f}")
    lines.append("")

    # Order KPIs
    order = kpis.get('orders', {})
    lines.append("ORDER METRICS")
    lines.append("-" * 40)
    lines.append(f"  Total Orders:            {order.get('total_orders', 0):>15,}")
    lines.append(f"  Orders Per Day:          {order.get('orders_per_day', 0):>15.1f}")
    lines.append(f"  Delivery Completion:     {order.get('delivery_completion_rate', 0):>15.1f}%")
    lines.append(f"  Cancellation Rate:       {order.get('cancellation_rate', 0):>15.1f}%")
    lines.append(f"  Avg Review Score:        {order.get('avg_review_score', 0):>15.2f}/5.0")
    lines.append(f"  Positive Review Rate:    {order.get('positive_review_rate', 0):>15.1f}%")
    lines.append("")
    lines.append("=" * 70)

    return "\n".join(lines)


def get_kpi_alerts(kpis: Dict[str, Any], thresholds: Dict[str, float] = None) -> list:
    """
    Generate alerts for KPIs that are outside acceptable thresholds.

    Args:
        kpis: Dictionary of KPIs
        thresholds: Custom threshold values (optional)

    Returns:
        List of alert messages
    """
    default_thresholds = {
        'delay_rate_high': 30.0,  # Alert if delay rate > 30%
        'cancellation_rate_high': 10.0,  # Alert if cancellation > 10%
        'repeat_rate_low': 20.0,  # Alert if repeat rate < 20%
        'review_score_low': 3.5,  # Alert if avg review < 3.5
        'on_time_delivery_low': 70.0,  # Alert if on-time < 70%
    }

    if thresholds:
        default_thresholds.update(thresholds)

    alerts = []

    # Check Delay Rate
    delay_rate = kpis.get('delivery', {}).get('delay_rate', 0)
    if delay_rate > default_thresholds['delay_rate_high']:
        alerts.append({
            'severity': 'HIGH',
            'metric': 'Delay Rate',
            'value': f"{delay_rate:.1f}%",
            'message': f"Delay rate ({delay_rate:.1f}%) exceeds threshold ({default_thresholds['delay_rate_high']}%)"
        })

    # Check Cancellation Rate
    cancellation_rate = kpis.get('orders', {}).get('cancellation_rate', 0)
    if cancellation_rate > default_thresholds['cancellation_rate_high']:
        alerts.append({
            'severity': 'HIGH',
            'metric': 'Cancellation Rate',
            'value': f"{cancellation_rate:.1f}%",
            'message': f"Cancellation rate ({cancellation_rate:.1f}%) exceeds threshold ({default_thresholds['cancellation_rate_high']}%)"
        })

    # Check Repeat Customer Rate
    repeat_rate = kpis.get('customers', {}).get('repeat_customer_rate', 0)
    if repeat_rate < default_thresholds['repeat_rate_low']:
        alerts.append({
            'severity': 'MEDIUM',
            'metric': 'Repeat Customer Rate',
            'value': f"{repeat_rate:.1f}%",
            'message': f"Repeat customer rate ({repeat_rate:.1f}%) below threshold ({default_thresholds['repeat_rate_low']}%)"
        })

    # Check Review Score
    review_score = kpis.get('orders', {}).get('avg_review_score', 0)
    if review_score < default_thresholds['review_score_low']:
        alerts.append({
            'severity': 'HIGH',
            'metric': 'Review Score',
            'value': f"{review_score:.2f}/5.0",
            'message': f"Average review score ({review_score:.2f}) below threshold ({default_thresholds['review_score_low']})"
        })

    # Check On-Time Delivery
    on_time_rate = kpis.get('delivery', {}).get('on_time_delivery_rate', 0)
    if on_time_rate < default_thresholds['on_time_delivery_low']:
        alerts.append({
            'severity': 'MEDIUM',
            'metric': 'On-Time Delivery',
            'value': f"{on_time_rate:.1f}%",
            'message': f"On-time delivery rate ({on_time_rate:.1f}%) below threshold ({default_thresholds['on_time_delivery_low']}%)"
        })

    return alerts


def create_kpi_scorecard(kpis: Dict[str, Any]) -> pd.DataFrame:
    """
    Create a KPI scorecard DataFrame for easy display.

    Args:
        kpis: Dictionary of KPIs

    Returns:
        DataFrame with KPI name, value, unit, and category
    """
    scorecard_data = []

    # Revenue KPIs
    rev = kpis.get('revenue', {})
    scorecard_data.append({'category': 'Revenue', 'kpi': 'Total Revenue', 'value': rev.get('total_revenue', 0), 'unit': 'USD'})
    scorecard_data.append({'category': 'Revenue', 'kpi': 'Avg Daily Revenue', 'value': rev.get('avg_daily_revenue', 0), 'unit': 'USD'})
    scorecard_data.append({'category': 'Revenue', 'kpi': 'Revenue Growth Rate', 'value': rev.get('revenue_growth_rate', 0), 'unit': '%'})
    scorecard_data.append({'category': 'Revenue', 'kpi': 'Revenue Per Customer', 'value': rev.get('revenue_per_customer', 0), 'unit': 'USD'})

    # Customer KPIs
    cust = kpis.get('customers', {})
    scorecard_data.append({'category': 'Customer', 'kpi': 'Total Customers', 'value': cust.get('total_customers', 0), 'unit': 'count'})
    scorecard_data.append({'category': 'Customer', 'kpi': 'Repeat Customer Rate', 'value': cust.get('repeat_customer_rate', 0), 'unit': '%'})
    scorecard_data.append({'category': 'Customer', 'kpi': 'Avg Orders Per Customer', 'value': cust.get('avg_orders_per_customer', 0), 'unit': 'count'})
    scorecard_data.append({'category': 'Customer', 'kpi': 'Avg Customer LTV', 'value': cust.get('avg_customer_lifetime_value', 0), 'unit': 'USD'})

    # Delivery KPIs
    del_kpis = kpis.get('delivery', {})
    scorecard_data.append({'category': 'Delivery', 'kpi': 'Avg Delivery Time', 'value': del_kpis.get('avg_delivery_time_days', 0), 'unit': 'days'})
    scorecard_data.append({'category': 'Delivery', 'kpi': 'On-Time Delivery Rate', 'value': del_kpis.get('on_time_delivery_rate', 0), 'unit': '%'})
    scorecard_data.append({'category': 'Delivery', 'kpi': 'Delay Rate', 'value': del_kpis.get('delay_rate', 0), 'unit': '%'})

    # Order KPIs
    order = kpis.get('orders', {})
    scorecard_data.append({'category': 'Order', 'kpi': 'Total Orders', 'value': order.get('total_orders', 0), 'unit': 'count'})
    scorecard_data.append({'category': 'Order', 'kpi': 'Avg Review Score', 'value': order.get('avg_review_score', 0), 'unit': 'score'})
    scorecard_data.append({'category': 'Order', 'kpi': 'Positive Review Rate', 'value': order.get('positive_review_rate', 0), 'unit': '%'})
    scorecard_data.append({'category': 'Order', 'kpi': 'Cancellation Rate', 'value': order.get('cancellation_rate', 0), 'unit': '%'})

    scorecard_df = pd.DataFrame(scorecard_data)
    return scorecard_df
