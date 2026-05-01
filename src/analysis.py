"""
Analysis Module

Business analysis functions for sales, customers, products, delivery, and payments.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def analyze_sales(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze sales performance metrics.

    Args:
        df: Merged DataFrame with order and item data

    Returns:
        Dictionary containing sales analysis results
    """
    results = {}

    # Calculate total revenue
    if 'price' in df.columns:
        results['total_revenue'] = df['price'].sum()
    else:
        results['total_revenue'] = 0

    # Monthly revenue trend
    if 'order_purchase_timestamp' in df.columns and 'price' in df.columns:
        df_valid = df.dropna(subset=['order_purchase_timestamp'])
        monthly_revenue = df_valid.groupby(
            df_valid['order_purchase_timestamp'].dt.to_period('M')
        )['price'].sum().reset_index()
        monthly_revenue.columns = ['month', 'revenue']
        results['monthly_revenue'] = monthly_revenue
    else:
        results['monthly_revenue'] = pd.DataFrame()

    # Top-selling categories
    if 'product_category_name_english' in df.columns and 'price' in df.columns:
        category_revenue = df.groupby('product_category_name_english')['price'].sum()
        results['top_categories'] = category_revenue.nlargest(10).reset_index()
        results['top_categories'].columns = ['category', 'revenue']
    else:
        results['top_categories'] = pd.DataFrame()

    # Average order value
    if 'order_id' in df.columns and 'price' in df.columns:
        order_values = df.groupby('order_id')['price'].sum()
        results['avg_order_value'] = order_values.mean()
    else:
        results['avg_order_value'] = 0

    # Total orders
    results['total_orders'] = df['order_id'].nunique() if 'order_id' in df.columns else 0

    return results


def analyze_customers(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze customer behavior and demographics.

    Args:
        df: Merged DataFrame with customer data

    Returns:
        Dictionary containing customer analysis results
    """
    results = {}

    # Unique customers
    if 'customer_id' in df.columns:
        results['unique_customers'] = df['customer_id'].nunique()
    else:
        results['unique_customers'] = 0

    # Repeat vs new customers (customers with more than one order)
    if 'customer_id' in df.columns and 'order_id' in df.columns:
        customer_orders = df.groupby('customer_id')['order_id'].nunique()
        results['repeat_customers'] = (customer_orders > 1).sum()
        results['new_customers'] = (customer_orders == 1).sum()
        results['repeat_rate'] = results['repeat_customers'] / results['unique_customers'] if results['unique_customers'] > 0 else 0
    else:
        results['repeat_customers'] = 0
        results['new_customers'] = 0
        results['repeat_rate'] = 0

    # Top cities by number of customers
    if 'customer_city' in df.columns:
        city_counts = df['customer_city'].value_counts().head(10)
        results['top_cities'] = city_counts.reset_index()
        results['top_cities'].columns = ['city', 'customers']
    else:
        results['top_cities'] = pd.DataFrame()

    # Top states by revenue
    if 'customer_state' in df.columns and 'price' in df.columns:
        state_revenue = df.groupby('customer_state')['price'].sum().nlargest(10)
        results['top_states'] = state_revenue.reset_index()
        results['top_states'].columns = ['state', 'revenue']
    else:
        results['top_states'] = pd.DataFrame()

    return results


def analyze_products(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze product performance metrics.

    Args:
        df: Merged DataFrame with product data

    Returns:
        Dictionary containing product analysis results
    """
    results = {}

    # Most sold products (by quantity)
    if 'product_id' in df.columns:
        product_sales = df.groupby('product_id').size()
        results['most_sold_products'] = product_sales.nlargest(10).reset_index()
        results['most_sold_products'].columns = ['product_id', 'quantity_sold']
    else:
        results['most_sold_products'] = pd.DataFrame()

    # Category performance (by quantity sold)
    if 'product_category_name_english' in df.columns:
        category_sales = df.groupby('product_category_name_english').size()
        results['category_by_quantity'] = category_sales.nlargest(10).reset_index()
        results['category_by_quantity'].columns = ['category', 'quantity']
    else:
        results['category_by_quantity'] = pd.DataFrame()

    # Average product price by category
    if 'product_category_name_english' in df.columns and 'price' in df.columns:
        category_price = df.groupby('product_category_name_english')['price'].mean()
        results['avg_price_by_category'] = category_price.nlargest(10).reset_index()
        results['avg_price_by_category'].columns = ['category', 'avg_price']
    else:
        results['avg_price_by_category'] = pd.DataFrame()

    return results


def analyze_delivery(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze delivery performance and efficiency.

    Args:
        df: Merged DataFrame with delivery data

    Returns:
        Dictionary containing delivery analysis results
    """
    results = {}

    # Calculate delivery time (order to delivered)
    df = df.copy()
    if 'order_purchase_timestamp' in df.columns and 'order_delivered_customer_date' in df.columns:
        df['delivery_time'] = (
            df['order_delivered_customer_date'] - df['order_purchase_timestamp']
        ).dt.days

        # Remove negative or extremely large delivery times (data errors)
        valid_delivery = df[(df['delivery_time'] >= 0) & (df['delivery_time'] <= 60)]

        if len(valid_delivery) > 0:
            results['avg_delivery_time'] = valid_delivery['delivery_time'].mean()
            results['median_delivery_time'] = valid_delivery['delivery_time'].median()
            results['delivery_time_std'] = valid_delivery['delivery_time'].std()
            results['delivery_times'] = valid_delivery['delivery_time'].dropna()
        else:
            results['avg_delivery_time'] = 0
            results['median_delivery_time'] = 0
            results['delivery_time_std'] = 0
            results['delivery_times'] = pd.Series()
    else:
        results['avg_delivery_time'] = 0
        results['median_delivery_time'] = 0
        results['delivery_time_std'] = 0
        results['delivery_times'] = pd.Series()

    # Delayed orders (delivered after estimated date)
    if 'order_delivered_customer_date' in df.columns and 'order_estimated_delivery_date' in df.columns:
        df['is_delayed'] = df['order_delivered_customer_date'] > df['order_estimated_delivery_date']
        results['delayed_orders'] = df['is_delayed'].sum()
        results['total_delivered'] = df['order_delivered_customer_date'].notna().sum()
        results['delay_rate'] = results['delayed_orders'] / results['total_delivered'] if results['total_delivered'] > 0 else 0
    else:
        results['delayed_orders'] = 0
        results['total_delivered'] = 0
        results['delay_rate'] = 0

    # Delivery time impact on review scores
    if 'review_score' in df.columns and 'delivery_time' in df.columns:
        valid_data = df.dropna(subset=['review_score', 'delivery_time'])
        if len(valid_data) > 0:
            results['delivery_review_correlation'] = valid_data['delivery_time'].corr(valid_data['review_score'])
        else:
            results['delivery_review_correlation'] = 0
    else:
        results['delivery_review_correlation'] = 0

    return results


def analyze_payments(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze payment methods and patterns.

    Args:
        df: Merged DataFrame with payment data

    Returns:
        Dictionary containing payment analysis results
    """
    results = {}

    # Payment type distribution
    if 'payment_type' in df.columns:
        payment_counts = df['payment_type'].value_counts()
        results['payment_type_distribution'] = payment_counts.reset_index()
        results['payment_type_distribution'].columns = ['payment_type', 'count']

        # Calculate percentages
        total = payment_counts.sum()
        results['payment_type_distribution']['percentage'] = (
            payment_counts / total * 100
        ).values
    else:
        results['payment_type_distribution'] = pd.DataFrame()

    # Payment value by type
    if 'payment_type' in df.columns and 'payment_value' in df.columns:
        payment_values = df.groupby('payment_type')['payment_value'].sum()
        results['payment_value_by_type'] = payment_values.reset_index()
        results['payment_value_by_type'].columns = ['payment_type', 'total_value']
    else:
        results['payment_value_by_type'] = pd.DataFrame()

    # Installment usage analysis
    if 'payment_installments' in df.columns:
        results['avg_installments'] = df['payment_installments'].mean()
        results['max_installments'] = df['payment_installments'].max()

        # Orders with installments
        installment_orders = df[df['payment_installments'] > 1]
        results['orders_with_installments'] = len(installment_orders)
        results['installment_rate'] = results['orders_with_installments'] / len(df) if len(df) > 0 else 0
    else:
        results['avg_installments'] = 0
        results['max_installments'] = 0
        results['orders_with_installments'] = 0
        results['installment_rate'] = 0

    return results


def generate_insights(analysis_results: Dict[str, Dict[str, Any]]) -> str:
    """
    Generate a comprehensive insights report from analysis results.

    Args:
        analysis_results: Dictionary containing all analysis results

    Returns:
        Formatted string report with key insights
    """
    report = []
    report.append("=" * 60)
    report.append("E-COMMERCE SALES ANALYSIS - BUSINESS INSIGHTS REPORT")
    report.append("=" * 60)
    report.append("")

    # Sales Insights
    if 'sales' in analysis_results:
        sales = analysis_results['sales']
        report.append("SALES PERFORMANCE")
        report.append("-" * 40)
        report.append(f"Total Revenue: ${sales.get('total_revenue', 0):,.2f}")
        report.append(f"Total Orders: {sales.get('total_orders', 0):,}")
        report.append(f"Average Order Value: ${sales.get('avg_order_value', 0):.2f}")
        report.append("")

        if 'top_categories' in sales and not sales['top_categories'].empty:
            report.append("Top 5 Product Categories by Revenue:")
            for idx, row in sales['top_categories'].head(5).iterrows():
                report.append(f"  - {row['category']}: ${row['revenue']:,.2f}")
            report.append("")

    # Customer Insights
    if 'customers' in analysis_results:
        customers = analysis_results['customers']
        report.append("CUSTOMER ANALYSIS")
        report.append("-" * 40)
        report.append(f"Unique Customers: {customers.get('unique_customers', 0):,}")
        report.append(f"Repeat Customers: {customers.get('repeat_customers', 0):,}")
        report.append(f"New Customers: {customers.get('new_customers', 0):,}")
        report.append(f"Customer Repeat Rate: {customers.get('repeat_rate', 0)*100:.1f}%")
        report.append("")

        if 'top_states' in customers and not customers['top_states'].empty:
            report.append("Top 5 States by Revenue:")
            for idx, row in customers['top_states'].head(5).iterrows():
                report.append(f"  - {row['state']}: ${row['revenue']:,.2f}")
            report.append("")

    # Product Insights
    if 'products' in analysis_results:
        products = analysis_results['products']
        report.append("PRODUCT PERFORMANCE")
        report.append("-" * 40)

        if 'category_by_quantity' in products and not products['category_by_quantity'].empty:
            report.append("Top 5 Categories by Units Sold:")
            for idx, row in products['category_by_quantity'].head(5).iterrows():
                report.append(f"  - {row['category']}: {row['quantity']:,} units")
            report.append("")

    # Delivery Insights
    if 'delivery' in analysis_results:
        delivery = analysis_results['delivery']
        report.append("DELIVERY PERFORMANCE")
        report.append("-" * 40)
        report.append(f"Average Delivery Time: {delivery.get('avg_delivery_time', 0):.1f} days")
        report.append(f"Median Delivery Time: {delivery.get('median_delivery_time', 0):.1f} days")
        report.append(f"Delay Rate: {delivery.get('delay_rate', 0)*100:.1f}%")

        corr = delivery.get('delivery_review_correlation', 0)
        if corr < -0.3:
            insight = "Strong negative correlation - delays significantly impact reviews"
        elif corr < -0.1:
            insight = "Moderate negative correlation - delays somewhat impact reviews"
        else:
            insight = "Weak correlation - delivery time has minimal impact on reviews"
        report.append(f"Delivery-Review Correlation: {corr:.3f} ({insight})")
        report.append("")

    # Payment Insights
    if 'payments' in analysis_results:
        payments = analysis_results['payments']
        report.append("PAYMENT ANALYSIS")
        report.append("-" * 40)

        if 'payment_type_distribution' in payments and not payments['payment_type_distribution'].empty:
            report.append("Payment Method Distribution:")
            for idx, row in payments['payment_type_distribution'].iterrows():
                report.append(f"  - {row['payment_type']}: {row['percentage']:.1f}%")
            report.append("")

        report.append(f"Average Installments: {payments.get('avg_installments', 0):.1f}")
        report.append(f"Orders Using Installments: {payments.get('installment_rate', 0)*100:.1f}%")
        report.append("")

    # Recommendations
    report.append("KEY RECOMMENDATIONS")
    report.append("-" * 40)
    report.append("1. Focus on top-performing categories for inventory optimization")
    report.append("2. Investigate delivery delays to improve customer satisfaction")
    report.append("3. Consider promotional campaigns for low-performing regions")
    report.append("4. Optimize payment options based on customer preferences")
    report.append("5. Implement loyalty programs to increase repeat customer rate")
    report.append("")
    report.append("=" * 60)
    report.append("End of Report")
    report.append("=" * 60)

    return "\n".join(report)


def generate_full_analysis(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Run all analyses and return comprehensive results.

    Args:
        df: Merged DataFrame

    Returns:
        Dictionary containing all analysis results
    """
    print("Running sales analysis...")
    sales_results = analyze_sales(df)

    print("Running customer analysis...")
    customer_results = analyze_customers(df)

    print("Running product analysis...")
    product_results = analyze_products(df)

    print("Running delivery analysis...")
    delivery_results = analyze_delivery(df)

    print("Running payment analysis...")
    payment_results = analyze_payments(df)

    return {
        'sales': sales_results,
        'customers': customer_results,
        'products': product_results,
        'delivery': delivery_results,
        'payments': payment_results
    }
