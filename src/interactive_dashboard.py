"""
Interactive Dashboard Module

Creates interactive HTML dashboards using Plotly for e-commerce analytics.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, Any, Optional
import os


def create_revenue_dashboard(df: pd.DataFrame) -> go.Figure:
    """
    Create interactive revenue dashboard with multiple views.

    Args:
        df: DataFrame with order_purchase_timestamp and price

    Returns:
        Plotly Figure object
    """
    if 'order_purchase_timestamp' not in df.columns or 'price' not in df.columns:
        return go.Figure().add_annotation(text="No revenue data available")

    df = df.copy()
    df = df.dropna(subset=['order_purchase_timestamp', 'price'])

    # Monthly revenue
    monthly_revenue = df.groupby(
        df['order_purchase_timestamp'].dt.to_period('M')
    )['price'].sum().reset_index()
    monthly_revenue.columns = ['month', 'revenue']
    monthly_revenue['month'] = monthly_revenue['month'].astype(str)

    # Daily revenue (last 30 days)
    df['date'] = df['order_purchase_timestamp'].dt.date
    daily_revenue = df.groupby('date')['price'].sum().reset_index()
    daily_revenue = daily_revenue.tail(30)

    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Monthly Revenue Trend', 'Daily Revenue (Last 30 Days)'),
        vertical_spacing=0.12,
        row_heights=[0.5, 0.5]
    )

    # Monthly revenue line
    fig.add_trace(
        go.Scatter(
            x=monthly_revenue['month'],
            y=monthly_revenue['revenue'],
            mode='lines+markers',
            name='Monthly Revenue',
            line=dict(color='#2E86AB', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
        ),
        row=1, col=1
    )

    # Daily revenue bar
    fig.add_trace(
        go.Bar(
            x=daily_revenue['date'].astype(str),
            y=daily_revenue['revenue'],
            name='Daily Revenue',
            marker_color='#198754',
            hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
        ),
        row=2, col=1
    )

    fig.update_layout(
        height=700,
        showlegend=False,
        title_text='<b>Revenue Dashboard</b>',
        title_font_size=20,
        hovermode='x unified'
    )

    fig.update_xaxes(tickangle=45, row=1, col=1)
    fig.update_xaxes(tickangle=45, row=2, col=1)

    fig.update_yaxes(title_text='Revenue ($)', row=1, col=1)
    fig.update_yaxes(title_text='Revenue ($)', row=2, col=1)

    return fig


def create_customer_dashboard(df: pd.DataFrame) -> go.Figure:
    """
    Create interactive customer analytics dashboard.

    Args:
        df: DataFrame with customer data

    Returns:
        Plotly Figure object
    """
    if 'customer_id' not in df.columns:
        return go.Figure().add_annotation(text="No customer data available")

    # Customer metrics
    customer_orders = df.groupby('customer_id')['order_id'].nunique()

    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Customer Order Distribution', 'Top 10 States',
                        'Customer Type', 'Top 10 Cities'),
        specs=[[{'type': 'histogram'}, {'type': 'bar'}],
               [{'type': 'pie'}, {'type': 'bar'}]]
    )

    # Order distribution histogram
    fig.add_trace(
        go.Histogram(
            x=customer_orders.values,
            name='Orders',
            marker_color='#6F42C1',
            nbinsx=20,
            hovertemplate='Orders: %{x}<br>Customers: %{y}<extra></extra>'
        ),
        row=1, col=1
    )

    # Top states bar chart
    if 'customer_state' in df.columns:
        state_counts = df['customer_state'].value_counts().head(10)
        fig.add_trace(
            go.Bar(
                x=state_counts.values,
                y=state_counts.index,
                orientation='h',
                name='States',
                marker_color='#FD7E14',
                hovertemplate='<b>%{y}</b><br>Customers: %{x}<extra></extra>'
            ),
            row=1, col=2
        )

    # Customer type pie chart
    repeat_customers = (customer_orders > 1).sum()
    new_customers = (customer_orders == 1).sum()

    fig.add_trace(
        go.Pie(
            labels=['New Customers', 'Repeat Customers'],
            values=[new_customers, repeat_customers],
            marker_colors=['#20C997', '#E83E8C'],
            hole=0.4,
            textinfo='label+percent',
            hovertemplate='%{label}: %{value:,} (%{percent})<extra></extra>'
        ),
        row=2, col=1
    )

    # Top cities
    if 'customer_city' in df.columns:
        city_counts = df['customer_city'].value_counts().head(10)
        fig.add_trace(
            go.Bar(
                x=city_counts.values,
                y=city_counts.index,
                orientation='h',
                name='Cities',
                marker_color='#0DCAF0',
                hovertemplate='<b>%{y}</b><br>Customers: %{x}<extra></extra>'
            ),
            row=2, col=2
        )

    fig.update_layout(
        height=800,
        showlegend=False,
        title_text='<b>Customer Analytics Dashboard</b>',
        title_font_size=20
    )

    fig.update_xaxes(title_text='Number of Customers', row=1, col=1)
    fig.update_xaxes(title_text='Number of Customers', row=1, col=2)
    fig.update_xaxes(title_text='Number of Customers', row=2, col=2)

    return fig


def create_product_dashboard(df: pd.DataFrame) -> go.Figure:
    """
    Create interactive product analytics dashboard.

    Args:
        df: DataFrame with product data

    Returns:
        Plotly Figure object
    """
    if 'product_id' not in df.columns:
        return go.Figure().add_annotation(text="No product data available")

    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Top 15 Categories by Revenue', 'Top 15 Categories by Units Sold',
                        'Revenue vs Units Scatter', 'Category Performance Heatmap'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{'type': 'scatter'}, {'type': 'heatmap'}]]
    )

    # Category revenue
    if 'product_category_name_english' in df.columns and 'price' in df.columns:
        category_revenue = df.groupby('product_category_name_english')['price'].sum().nlargest(15)

        fig.add_trace(
            go.Bar(
                x=category_revenue.values,
                y=[cat.replace('_', ' ').title() for cat in category_revenue.index],
                orientation='h',
                name='Revenue',
                marker_color='#6610F2',
                hovertemplate='<b>%{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>'
            ),
            row=1, col=1
        )

        # Category units
        category_units = df.groupby('product_category_name_english').size().nlargest(15)

        fig.add_trace(
            go.Bar(
                x=category_units.values,
                y=[cat.replace('_', ' ').title() for cat in category_units.index],
                orientation='h',
                name='Units',
                marker_color='#20C997',
                hovertemplate='<b>%{y}</b><br>Units: %{x:,}<extra></extra>'
            ),
            row=1, col=2
        )

        # Scatter plot - Revenue vs Units
        category_stats = df.groupby('product_category_name_english').agg({
            'price': 'sum',
            'product_id': 'count'
        }).reset_index()
        category_stats.columns = ['category', 'revenue', 'units']

        fig.add_trace(
            go.Scatter(
                x=category_stats['units'],
                y=category_stats['revenue'],
                mode='markers+text',
                text=category_stats['category'].str.replace('_', ' ').str.title(),
                textposition='top center',
                marker=dict(
                    size=category_stats['revenue'] / category_stats['revenue'].max() * 50 + 10,
                    color=category_stats['revenue'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title='Revenue ($)')
                ),
                name='Categories',
                hovertemplate='<b>%{text}</b><br>Units: %{x:,}<br>Revenue: $%{y:,.2f}<extra></extra>'
            ),
            row=2, col=1
        )

    fig.update_layout(
        height=900,
        showlegend=False,
        title_text='<b>Product Analytics Dashboard</b>',
        title_font_size=20
    )

    fig.update_xaxes(title_text='Revenue ($)', row=1, col=1)
    fig.update_xaxes(title_text='Units Sold', row=1, col=2)
    fig.update_xaxes(title_text='Units Sold', row=2, col=1)
    fig.update_yaxes(title_text='Revenue ($)', row=2, col=1)

    return fig


def create_delivery_dashboard(df: pd.DataFrame) -> go.Figure:
    """
    Create interactive delivery performance dashboard.

    Args:
        df: DataFrame with delivery data

    Returns:
        Plotly Figure object
    """
    # Calculate delivery times
    if 'order_purchase_timestamp' not in df.columns or 'order_delivered_customer_date' not in df.columns:
        return go.Figure().add_annotation(text="No delivery data available")

    df = df.copy()
    df = df.dropna(subset=['order_purchase_timestamp', 'order_delivered_customer_date'])

    df['delivery_time'] = (
        df['order_delivered_customer_date'] - df['order_purchase_timestamp']
    ).dt.days

    valid_delivery = df[(df['delivery_time'] >= 0) & (df['delivery_time'] <= 60)]

    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Delivery Time Distribution', 'Delivery Time by Month',
                        'On-Time vs Delayed', 'Delivery Time Box Plot'),
        specs=[[{'type': 'histogram'}, {'type': 'scatter'}],
               [{'type': 'pie'}, {'type': 'box'}]]
    )

    # Delivery time histogram
    fig.add_trace(
        go.Histogram(
            x=valid_delivery['delivery_time'],
            name='Delivery Time',
            marker_color='#DC3545',
            nbinsx=30,
            hovertemplate='Days: %{x}<br>Orders: %{y}<extra></extra>'
        ),
        row=1, col=1
    )

    # Monthly delivery time trend
    valid_delivery_copy = valid_delivery.copy()
    valid_delivery_copy['month'] = valid_delivery_copy['order_purchase_timestamp'].dt.to_period('M').astype(str)
    monthly_delivery = valid_delivery_copy.groupby('month')['delivery_time'].mean().reset_index()

    fig.add_trace(
        go.Scatter(
            x=monthly_delivery['month'],
            y=monthly_delivery['delivery_time'],
            mode='lines+markers',
            name='Avg Delivery Time',
            line=dict(color='#0D6EFD', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>Avg Days: %{y:.1f}<extra></extra>'
        ),
        row=1, col=2
    )

    # On-time vs Delayed pie chart
    if 'order_estimated_delivery_date' in df.columns:
        df_valid = df.dropna(subset=['order_estimated_delivery_date'])
        on_time = (df_valid['order_delivered_customer_date'] <= df_valid['order_estimated_delivery_date']).sum()
        delayed = len(df_valid) - on_time

        fig.add_trace(
            go.Pie(
                labels=['On-Time', 'Delayed'],
                values=[on_time, delayed],
                marker_colors=['#198754', '#DC3545'],
                hole=0.4,
                textinfo='label+percent',
                hovertemplate='%{label}: %{value:,} (%{percent})<extra></extra>'
            ),
            row=2, col=1
        )

    # Box plot
    fig.add_trace(
        go.Box(
            y=valid_delivery['delivery_time'],
            name='Delivery Time',
            marker_color='#FFC107',
            boxpoints='outliers',
            hovertemplate='Min: %{ymin}<br>Q1: %{q1}<br>Median: %{median}<br>Q3: %{q3}<br>Max: %{ymax}<extra></extra>'
        ),
        row=2, col=2
    )

    fig.update_layout(
        height=800,
        showlegend=False,
        title_text='<b>Delivery Performance Dashboard</b>',
        title_font_size=20
    )

    fig.update_xaxes(title_text='Delivery Time (days)', row=1, col=1)
    fig.update_xaxes(title_text='Month', row=1, col=2)
    fig.update_yaxes(title_text='Number of Orders', row=1, col=1)
    fig.update_yaxes(title_text='Avg Delivery Time (days)', row=1, col=2)
    fig.update_yaxes(title_text='Delivery Time (days)', row=2, col=2)

    return fig


def create_payment_dashboard(df: pd.DataFrame) -> go.Figure:
    """
    Create interactive payment analytics dashboard.

    Args:
        df: DataFrame with payment data

    Returns:
        Plotly Figure object
    """
    if 'payment_type' not in df.columns:
        return go.Figure().add_annotation(text="No payment data available")

    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Payment Method Distribution', 'Payment Value by Type',
                        'Installment Distribution', 'Payment Type Trends'),
        specs=[[{'type': 'pie'}, {'type': 'bar'}],
               [{'type': 'histogram'}, {'type': 'bar'}]]
    )

    # Payment type pie chart
    payment_counts = df['payment_type'].value_counts()

    fig.add_trace(
        go.Pie(
            labels=[pt.replace('_', ' ').title() for pt in payment_counts.index],
            values=payment_counts.values,
            marker_colors=px.colors.qualitative.Set2,
            hole=0.4,
            textinfo='label+percent',
            hovertemplate='%{label}: %{value:,} (%{percent})<extra></extra>'
        ),
        row=1, col=1
    )

    # Payment value by type
    if 'payment_value' in df.columns:
        payment_values = df.groupby('payment_type')['payment_value'].sum()

        fig.add_trace(
            go.Bar(
                x=[pt.replace('_', ' ').title() for pt in payment_values.index],
                y=payment_values.values,
                name='Value',
                marker_color=px.colors.qualitative.Bold,
                hovertemplate='<b>%{x}</b><br>Total: $%{y:,.2f}<extra></extra>'
            ),
            row=1, col=2
        )

    # Installment distribution
    if 'payment_installments' in df.columns:
        installment_dist = df['payment_installments'].value_counts().sort_index()

        fig.add_trace(
            go.Histogram(
                x=df['payment_installments'],
                name='Installments',
                marker_color='#6F42C1',
                nbinsx=12,
                hovertemplate='Installments: %{x}<br>Orders: %{y}<extra></extra>'
            ),
            row=2, col=1
        )

    # Average payment value by type
    if 'payment_value' in df.columns:
        avg_payment = df.groupby('payment_type')['payment_value'].mean()

        fig.add_trace(
            go.Bar(
                x=[pt.replace('_', ' ').title() for pt in avg_payment.index],
                y=avg_payment.values,
                name='Avg Value',
                marker_color='#FD7E14',
                hovertemplate='<b>%{x}</b><br>Avg: $%{y:,.2f}<extra></extra>'
            ),
            row=2, col=2
        )

    fig.update_layout(
        height=800,
        showlegend=False,
        title_text='<b>Payment Analytics Dashboard</b>',
        title_font_size=20
    )

    fig.update_xaxes(title_text='Payment Method', row=1, col=2)
    fig.update_xaxes(title_text='Number of Installments', row=2, col=1)
    fig.update_xaxes(title_text='Payment Method', row=2, col=2)
    fig.update_yaxes(title_text='Total Value ($)', row=1, col=2)
    fig.update_yaxes(title_text='Number of Orders', row=2, col=1)
    fig.update_yaxes(title_text='Avg Value ($)', row=2, col=2)

    return fig


def create_executive_summary_dashboard(df: pd.DataFrame, kpis: Dict[str, Any]) -> go.Figure:
    """
    Create executive summary dashboard with key metrics.

    Args:
        df: DataFrame with all data
        kpis: Dictionary of calculated KPIs

    Returns:
        Plotly Figure object
    """
    # Create summary metrics
    metrics = []

    # Revenue metrics
    rev = kpis.get('revenue', {})
    metrics.append({
        'metric': 'Total Revenue',
        'value': f"${rev.get('total_revenue', 0):,.0f}",
        'category': 'Revenue'
    })
    metrics.append({
        'metric': 'Avg Order Value',
        'value': f"${rev.get('avg_ticket_value', 0):,.0f}",
        'category': 'Revenue'
    })

    # Customer metrics
    cust = kpis.get('customers', {})
    metrics.append({
        'metric': 'Total Customers',
        'value': f"{cust.get('total_customers', 0):,}",
        'category': 'Customer'
    })
    metrics.append({
        'metric': 'Repeat Rate',
        'value': f"{cust.get('repeat_customer_rate', 0):.1f}%",
        'category': 'Customer'
    })

    # Delivery metrics
    delivery = kpis.get('delivery', {})
    metrics.append({
        'metric': 'On-Time Delivery',
        'value': f"{delivery.get('on_time_delivery_rate', 0):.1f}%",
        'category': 'Delivery'
    })
    metrics.append({
        'metric': 'Avg Delivery Time',
        'value': f"{delivery.get('avg_delivery_time_days', 0):.1f} days",
        'category': 'Delivery'
    })

    # Order metrics
    order = kpis.get('orders', {})
    metrics.append({
        'metric': 'Avg Review Score',
        'value': f"{order.get('avg_review_score', 0):.2f}/5",
        'category': 'Quality'
    })
    metrics.append({
        'metric': 'Orders',
        'value': f"{order.get('total_orders', 0):,}",
        'category': 'Order'
    })

    # Create gauge charts for key metrics
    fig = make_subplots(
        rows=2, cols=4,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}],
               [{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]],
        subplot_titles=[m['metric'] for m in metrics]
    )

    colors = ['#2E86AB', '#198754', '#FD7E14', '#6F42C1',
              '#DC3545', '#0DCAF0', '#20C997', '#E83E8C']

    for i, m in enumerate(metrics):
        row = (i // 4) + 1
        col = (i % 4) + 1

        # Parse value
        value_str = m['value'].replace('$', '').replace(',', '').replace(' days', '').replace('/5', '')
        try:
            value = float(value_str)
        except:
            value = 0

        # Determine max value for gauge
        if 'Revenue' in m['metric'] or 'Order Value' in m['metric']:
            max_val = value * 1.5
        elif 'Rate' in m['metric'] or '%' in m['value']:
            max_val = 100
        elif 'Score' in m['metric']:
            max_val = 5
        elif 'days' in m['value']:
            max_val = 30
        else:
            max_val = value * 1.5 if value > 0 else 100

        fig.add_trace(
            go.Indicator(
                mode='number+gauge',
                value=value,
                number={'valueformat': ',.0f' if value > 100 else '.1f'},
                gauge={
                    'axis': {'range': [0, max_val]},
                    'bar': {'color': colors[i]},
                    'bgcolor': 'white',
                    'borderwidth': 2,
                    'bordercolor': 'gray'
                }
            ),
            row=row, col=col
        )

    fig.update_layout(
        height=500,
        title_text='<b>Executive Summary - Key Performance Indicators</b>',
        title_font_size=20
    )

    return fig


def save_dashboard(fig: go.Figure, output_path: str) -> str:
    """
    Save dashboard to HTML file.

    Args:
        fig: Plotly Figure object
        output_path: Path to save HTML file

    Returns:
        Path to saved file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fig.write_html(output_path, include_plotlyjs='cdn', full_html=True)
    return output_path


def create_full_dashboard(df: pd.DataFrame, kpis: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    """
    Create and save all interactive dashboards.

    Args:
        df: Merged DataFrame
        kpis: Dictionary of calculated KPIs
        output_dir: Directory to save HTML files

    Returns:
        Dictionary mapping dashboard names to file paths
    """
    os.makedirs(output_dir, exist_ok=True)

    saved_dashboards = {}

    print("Creating revenue dashboard...")
    fig = create_revenue_dashboard(df)
    saved_dashboards['revenue'] = save_dashboard(fig, os.path.join(output_dir, 'revenue_dashboard.html'))

    print("Creating customer dashboard...")
    fig = create_customer_dashboard(df)
    saved_dashboards['customer'] = save_dashboard(fig, os.path.join(output_dir, 'customer_dashboard.html'))

    print("Creating product dashboard...")
    fig = create_product_dashboard(df)
    saved_dashboards['product'] = save_dashboard(fig, os.path.join(output_dir, 'product_dashboard.html'))

    print("Creating delivery dashboard...")
    fig = create_delivery_dashboard(df)
    saved_dashboards['delivery'] = save_dashboard(fig, os.path.join(output_dir, 'delivery_dashboard.html'))

    print("Creating payment dashboard...")
    fig = create_payment_dashboard(df)
    saved_dashboards['payment'] = save_dashboard(fig, os.path.join(output_dir, 'payment_dashboard.html'))

    print("Creating executive summary dashboard...")
    fig = create_executive_summary_dashboard(df, kpis)
    saved_dashboards['executive_summary'] = save_dashboard(fig, os.path.join(output_dir, 'executive_summary.html'))

    print(f"\nSaved {len(saved_dashboards)} interactive dashboards to {output_dir}")
    return saved_dashboards
