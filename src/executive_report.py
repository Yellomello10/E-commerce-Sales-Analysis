"""
Executive Report Generator

Creates comprehensive executive summary reports with actionable recommendations.
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, Any

from .kpi_dashboard import calculate_kpis, get_kpi_alerts
from .advanced_insights import (
    perform_rfm_segmentation,
    calculate_churn_risk,
    generate_advanced_insights_report
)


def generate_executive_summary(df: pd.DataFrame, kpis: Dict[str, Any] = None) -> str:
    """
    Generate comprehensive executive summary report.

    Args:
        df: Merged DataFrame
        kpis: Pre-calculated KPIs (optional)

    Returns:
        Formatted string executive summary
    """
    if kpis is None:
        kpis = calculate_kpis(df)

    lines = []

    # Header
    lines.append("=" * 80)
    lines.append("                    EXECUTIVE SUMMARY REPORT")
    lines.append("                    E-Commerce Sales Analysis")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Data Period: {df['order_purchase_timestamp'].min().strftime('%Y-%m-%d')} to {df['order_purchase_timestamp'].max().strftime('%Y-%m-%d')}")
    lines.append(f"Total Records Analyzed: {len(df):,}")
    lines.append("")

    # Executive Overview
    lines.append("-" * 80)
    lines.append("EXECUTIVE OVERVIEW")
    lines.append("-" * 80)
    lines.append("")

    rev = kpis.get('revenue', {})
    cust = kpis.get('customers', {})
    order = kpis.get('orders', {})
    delivery = kpis.get('delivery', {})

    lines.append(f"This report analyzes {kpis['orders']['total_orders']:,} orders from ")
    lines.append(f"{kpis['customers']['total_customers']:,} unique customers, generating ")
    lines.append(f"${kpis['revenue']['total_revenue']:,.2f} in total revenue.")
    lines.append("")

    # Key Highlights
    lines.append("KEY HIGHLIGHTS:")
    lines.append(f"  * Average order value: ${rev['avg_ticket_value']:.2f}")
    lines.append(f"  * Customer repeat rate: {cust['repeat_customer_rate']:.1f}%")
    lines.append(f"  * On-time delivery rate: {delivery['on_time_delivery_rate']:.1f}%")
    lines.append(f"  * Average review score: {order['avg_review_score']:.2f}/5.0")
    lines.append("")

    # Performance Scorecard
    lines.append("-" * 80)
    lines.append("PERFORMANCE SCORECARD")
    lines.append("-" * 80)
    lines.append("")

    # Calculate overall performance score
    scores = []

    # Revenue health (based on growth rate)
    growth_rate = rev.get('revenue_growth_rate', 0)
    if growth_rate > 10:
        scores.append(('Revenue Growth', 'Excellent', growth_rate))
    elif growth_rate > 5:
        scores.append(('Revenue Growth', 'Good', growth_rate))
    elif growth_rate > 0:
        scores.append(('Revenue Growth', 'Neutral', growth_rate))
    else:
        scores.append(('Revenue Growth', 'Needs Attention', growth_rate))

    # Customer loyalty
    repeat_rate = cust.get('repeat_customer_rate', 0)
    if repeat_rate > 50:
        scores.append(('Customer Loyalty', 'Excellent', repeat_rate))
    elif repeat_rate > 30:
        scores.append(('Customer Loyalty', 'Good', repeat_rate))
    elif repeat_rate > 20:
        scores.append(('Customer Loyalty', 'Neutral', repeat_rate))
    else:
        scores.append(('Customer Loyalty', 'Needs Attention', repeat_rate))

    # Delivery performance
    on_time = delivery.get('on_time_delivery_rate', 0)
    if on_time > 90:
        scores.append(('Delivery Performance', 'Excellent', on_time))
    elif on_time > 80:
        scores.append(('Delivery Performance', 'Good', on_time))
    elif on_time > 70:
        scores.append(('Delivery Performance', 'Neutral', on_time))
    else:
        scores.append(('Delivery Performance', 'Needs Attention', on_time))

    # Customer satisfaction
    review_score = order.get('avg_review_score', 0)
    if review_score >= 4.5:
        scores.append(('Customer Satisfaction', 'Excellent', review_score))
    elif review_score >= 4.0:
        scores.append(('Customer Satisfaction', 'Good', review_score))
    elif review_score >= 3.5:
        scores.append(('Customer Satisfaction', 'Neutral', review_score))
    else:
        scores.append(('Customer Satisfaction', 'Needs Attention', review_score))

    lines.append(f"  {'Metric':<25} {'Status':<20} {'Value':<15}")
    lines.append(f"  {'-'*25} {'-'*20} {'-'*15}")

    for metric, status, value in scores:
        value_display = f"{value:.1f}%" if '%' in metric or 'Rate' in metric else f"{value:.2f}"
        lines.append(f"  {metric:<25} {status:<20} {value_display:<15}")

    lines.append("")

    # KPI Alerts
    alerts = get_kpi_alerts(kpis)
    if alerts:
        lines.append("-" * 80)
        lines.append("ATTENTION REQUIRED - KPI ALERTS")
        lines.append("-" * 80)
        lines.append("")

        for alert in alerts:
            severity_icon = "[!!]" if alert['severity'] == 'HIGH' else "[!]"
            lines.append(f"  {severity_icon} {alert['severity']}: {alert['message']}")

        lines.append("")

    # Strategic Recommendations
    lines.append("-" * 80)
    lines.append("STRATEGIC RECOMMENDATIONS")
    lines.append("-" * 80)
    lines.append("")

    recommendations = generate_strategic_recommendations(kpis, df)

    for i, rec in enumerate(recommendations, 1):
        priority = rec.get('priority', 'Medium')
        priority_icon = "[HIGH]" if priority == 'High' else "[MED]" if priority == 'Medium' else "[LOW]"
        lines.append(f"  {i}. {priority_icon} {rec['title']}")
        lines.append(f"     {rec['description']}")
        lines.append(f"     Expected Impact: {rec['impact']}")
        lines.append("")

    # Financial Summary
    lines.append("-" * 80)
    lines.append("FINANCIAL SUMMARY")
    lines.append("-" * 80)
    lines.append("")

    lines.append(f"  Total Revenue:              ${rev['total_revenue']:>15,.2f}")
    lines.append(f"  Average Daily Revenue:      ${rev['avg_daily_revenue']:>15,.2f}")
    lines.append(f"  Revenue Per Customer:       ${rev['revenue_per_customer']:>15,.2f}")
    lines.append(f"  Average Order Value:        ${rev['avg_ticket_value']:>15,.2f}")
    lines.append(f"  Revenue Growth Rate:        {rev['revenue_growth_rate']:>15.1f}%")
    lines.append("")

    # Customer Insights
    lines.append("-" * 80)
    lines.append("CUSTOMER INSIGHTS")
    lines.append("-" * 80)
    lines.append("")

    lines.append(f"  Total Unique Customers:     {cust['total_customers']:>15,}")
    lines.append(f"  New Customers:              {cust['new_customers']:>15,}")
    lines.append(f"  Repeat Customers:           {cust['repeat_customers']:>15,}")
    lines.append(f"  Repeat Customer Rate:       {cust['repeat_customer_rate']:>15.1f}%")
    lines.append(f"  Avg Orders Per Customer:    {cust['avg_orders_per_customer']:>15.2f}")
    lines.append(f"  Avg Customer Lifetime Value:${cust['avg_customer_lifetime_value']:>15,.2f}")
    lines.append("")

    # Operational Metrics
    lines.append("-" * 80)
    lines.append("OPERATIONAL METRICS")
    lines.append("-" * 80)
    lines.append("")

    lines.append(f"  Average Delivery Time:      {delivery['avg_delivery_time_days']:>15.1f} days")
    lines.append(f"  On-Time Delivery Rate:      {delivery['on_time_delivery_rate']:>15.1f}%")
    lines.append(f"  Delay Rate:                 {delivery['delay_rate']:>15.1f}%")
    lines.append(f"  Average Freight Value:      ${delivery['avg_freight_value']:>15,.2f}")
    lines.append(f"  Orders Per Day:             {order['orders_per_day']:>15.1f}")
    lines.append(f"  Cancellation Rate:          {order['cancellation_rate']:>15.1f}%")
    lines.append("")

    # Product Performance
    lines.append("-" * 80)
    lines.append("PRODUCT PERFORMANCE")
    lines.append("-" * 80)
    lines.append("")

    prod = kpis.get('products', {})
    lines.append(f"  Total Items Sold:           {prod['total_items_sold']:>15,}")
    lines.append(f"  Unique Products Sold:       {prod['unique_products_sold']:>15,}")
    lines.append(f"  Avg Items Per Order:        {prod['avg_items_per_order']:>15.2f}")
    lines.append(f"  Top 10 Product Concentration: {prod['top_10_product_concentration']:>10.1f}%")
    lines.append("")

    # Payment Analysis
    pay = kpis.get('payments', {})
    lines.append("-" * 80)
    lines.append("PAYMENT ANALYSIS")
    lines.append("-" * 80)
    lines.append("")

    lines.append(f"  Credit Card Usage:          {pay['credit_card_usage_rate']:>15.1f}%")
    lines.append(f"  Average Installments:       {pay['avg_installments']:>15.1f}x")
    lines.append(f"  Installment Usage Rate:     {pay['installment_usage_rate']:>15.1f}%")
    lines.append(f"  Average Payment Value:      ${pay['avg_payment_value']:>15,.2f}")
    lines.append("")

    # Risk Assessment
    lines.append("-" * 80)
    lines.append("RISK ASSESSMENT")
    lines.append("-" * 80)
    lines.append("")

    # Calculate risk level
    risk_factors = []
    if delivery.get('delay_rate', 0) > 30:
        risk_factors.append("High delivery delay rate impacting customer satisfaction")
    if cust.get('repeat_customer_rate', 0) < 20:
        risk_factors.append("Low customer retention - dependency on new customer acquisition")
    if order.get('cancellation_rate', 0) > 10:
        risk_factors.append("High order cancellation rate")
    if order.get('avg_review_score', 0) < 3.5:
        risk_factors.append("Low customer satisfaction scores")

    if risk_factors:
        lines.append("  Identified Risks:")
        for risk in risk_factors:
            lines.append(f"    - {risk}")
    else:
        lines.append("  No significant risks identified. Key metrics are within healthy ranges.")

    lines.append("")

    # Action Items
    lines.append("-" * 80)
    lines.append("PRIORITY ACTION ITEMS")
    lines.append("-" * 80)
    lines.append("")

    action_items = generate_action_items(kpis)
    for i, item in enumerate(action_items, 1):
        lines.append(f"  {i}. {item}")

    lines.append("")
    lines.append("=" * 80)
    lines.append("                         END OF EXECUTIVE SUMMARY")
    lines.append("=" * 80)

    return "\n".join(lines)


def generate_strategic_recommendations(kpis: Dict[str, Any], df: pd.DataFrame) -> list:
    """
    Generate strategic recommendations based on KPI analysis.

    Args:
        kpis: Dictionary of KPIs
        df: Merged DataFrame

    Returns:
        List of recommendation dictionaries
    """
    recommendations = []

    # Customer retention recommendations
    cust = kpis.get('customers', {})
    if cust.get('repeat_customer_rate', 0) < 30:
        recommendations.append({
            'priority': 'High',
            'title': 'Improve Customer Retention',
            'description': 'Implement a customer loyalty program with tiered rewards to increase repeat purchase rate. Consider personalized email campaigns and exclusive offers for returning customers.',
            'impact': 'Potential 15-25% increase in customer lifetime value'
        })

    # Delivery optimization
    delivery = kpis.get('delivery', {})
    if delivery.get('delay_rate', 0) > 20:
        recommendations.append({
            'priority': 'High',
            'title': 'Optimize Delivery Operations',
            'description': 'Review logistics partnerships and consider regional distribution centers. Implement proactive delay notifications and compensation policies.',
            'impact': 'Improved customer satisfaction and reduced churn'
        })

    # Product concentration risk
    prod = kpis.get('products', {})
    if prod.get('top_10_product_concentration', 0) > 50:
        recommendations.append({
            'priority': 'Medium',
            'title': 'Diversify Product Portfolio',
            'description': 'Reduce dependency on top-selling products by promoting underperforming categories. Consider bundle offers and cross-selling strategies.',
            'impact': 'Reduced business risk and increased average order value'
        })

    # Payment optimization
    pay = kpis.get('payments', {})
    if pay.get('installment_usage_rate', 0) > 60:
        recommendations.append({
            'priority': 'Medium',
            'title': 'Optimize Payment Strategy',
            'description': 'Analyze profitability of installment payments. Consider offering discounts for upfront payments to improve cash flow.',
            'impact': 'Improved cash flow and reduced payment processing costs'
        })

    # Review score improvement
    order = kpis.get('orders', {})
    if order.get('avg_review_score', 0) < 4.0:
        recommendations.append({
            'priority': 'High',
            'title': 'Enhance Customer Experience',
            'description': 'Implement systematic review analysis to identify pain points. Focus on product quality, accurate descriptions, and customer service improvements.',
            'impact': 'Higher conversion rates and customer loyalty'
        })

    # Always add growth recommendation
    recommendations.append({
        'priority': 'Medium',
        'title': 'Leverage Data for Growth',
        'description': 'Use customer segmentation (RFM analysis) to target high-value customers with personalized campaigns. Implement predictive analytics for inventory optimization.',
        'impact': 'Data-driven decision making for sustainable growth'
    })

    return recommendations


def generate_action_items(kpis: Dict[str, Any]) -> list:
    """
    Generate specific action items based on KPI analysis.

    Args:
        kpis: Dictionary of KPIs

    Returns:
        List of action item strings
    """
    action_items = []

    # Based on delivery performance
    if kpis.get('delivery', {}).get('delay_rate', 0) > 25:
        action_items.append("URGENT: Conduct root cause analysis of delivery delays within 7 days")

    # Based on customer metrics
    if kpis.get('customers', {}).get('repeat_customer_rate', 0) < 25:
        action_items.append("Launch customer retention campaign within 14 days")

    # Based on review scores
    if kpis.get('orders', {}).get('avg_review_score', 0) < 3.8:
        action_items.append("Initiate customer satisfaction survey and action plan")

    # Based on cancellation rate
    if kpis.get('orders', {}).get('cancellation_rate', 0) > 8:
        action_items.append("Review and address top cancellation reasons")

    # Standard action items
    action_items.append("Schedule monthly KPI review meeting with stakeholders")
    action_items.append("Prepare detailed category performance analysis for next quarter")
    action_items.append("Evaluate logistics partners for potential cost optimization")

    return action_items


def save_executive_report(df: pd.DataFrame, output_path: str) -> str:
    """
    Generate and save executive summary report.

    Args:
        df: Merged DataFrame
        output_path: Path to save the report

    Returns:
        Path to saved report
    """
    kpis = calculate_kpis(df)
    report = generate_executive_summary(df, kpis)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    # Also generate advanced insights report
    advanced_report = generate_advanced_insights_report(df)

    advanced_path = output_path.replace('.txt', '_advanced.txt')
    with open(advanced_path, 'w', encoding='utf-8') as f:
        f.write(advanced_report)

    print(f"Executive summary saved to: {output_path}")
    print(f"Advanced insights saved to: {advanced_path}")

    return output_path
