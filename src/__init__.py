"""
E-commerce Sales Analysis Package

A comprehensive data analytics package for analyzing Brazilian e-commerce data.
Includes KPI dashboards, advanced insights, and interactive visualizations.
"""

from .data_cleaning import load_data, clean_data, merge_data, save_processed_data
from .analysis import (
    analyze_sales,
    analyze_customers,
    analyze_products,
    analyze_delivery,
    analyze_payments,
    generate_insights,
    generate_full_analysis
)
from .visualization import (
    plot_revenue_trend,
    plot_top_categories,
    plot_payment_types,
    plot_correlation_heatmap,
    plot_delivery_histogram,
    plot_customer_geography,
    save_all_charts
)
from .kpi_dashboard import (
    calculate_kpis,
    calculate_revenue_kpis,
    calculate_customer_kpis,
    calculate_product_kpis,
    calculate_delivery_kpis,
    calculate_payment_kpis,
    calculate_order_kpis,
    generate_kpi_summary,
    get_kpi_alerts,
    create_kpi_scorecard
)
from .advanced_insights import (
    perform_cohort_analysis,
    perform_rfm_segmentation,
    calculate_customer_lifetime_value,
    forecast_sales,
    analyze_product_affinity,
    calculate_churn_risk,
    analyze_customer_journey,
    generate_advanced_insights_report
)
from .interactive_dashboard import (
    create_revenue_dashboard,
    create_customer_dashboard,
    create_product_dashboard,
    create_delivery_dashboard,
    create_payment_dashboard,
    create_executive_summary_dashboard,
    save_dashboard,
    create_full_dashboard
)

__all__ = [
    # Data Cleaning
    'load_data',
    'clean_data',
    'merge_data',
    'save_processed_data',

    # Analysis
    'analyze_sales',
    'analyze_customers',
    'analyze_products',
    'analyze_delivery',
    'analyze_payments',
    'generate_insights',
    'generate_full_analysis',

    # Visualization
    'plot_revenue_trend',
    'plot_top_categories',
    'plot_payment_types',
    'plot_correlation_heatmap',
    'plot_delivery_histogram',
    'plot_customer_geography',
    'save_all_charts',

    # KPI Dashboard
    'calculate_kpis',
    'calculate_revenue_kpis',
    'calculate_customer_kpis',
    'calculate_product_kpis',
    'calculate_delivery_kpis',
    'calculate_payment_kpis',
    'calculate_order_kpis',
    'generate_kpi_summary',
    'get_kpi_alerts',
    'create_kpi_scorecard',

    # Advanced Insights
    'perform_cohort_analysis',
    'perform_rfm_segmentation',
    'calculate_customer_lifetime_value',
    'forecast_sales',
    'analyze_product_affinity',
    'calculate_churn_risk',
    'analyze_customer_journey',
    'generate_advanced_insights_report',

    # Interactive Dashboard
    'create_revenue_dashboard',
    'create_customer_dashboard',
    'create_product_dashboard',
    'create_delivery_dashboard',
    'create_payment_dashboard',
    'create_executive_summary_dashboard',
    'save_dashboard',
    'create_full_dashboard'
]
