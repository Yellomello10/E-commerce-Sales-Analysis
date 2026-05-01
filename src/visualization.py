"""
Visualization Module

Chart generation functions for e-commerce data analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import Optional


# Set consistent styling for all visualizations
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


def plot_revenue_trend(df: pd.DataFrame, save_path: str,
                       monthly_data: Optional[pd.DataFrame] = None) -> str:
    """
    Create line chart showing monthly revenue trend.

    Args:
        df: DataFrame with order_purchase_timestamp and price columns
        save_path: Path to save the chart image
        monthly_data: Pre-computed monthly revenue data (optional)

    Returns:
        Path to saved chart
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    if monthly_data is not None and not monthly_data.empty:
        data = monthly_data
        ax.plot(data['month'].astype(str), data['revenue'],
                marker='o', linewidth=2, markersize=6, color='#2E86AB')
    elif 'order_purchase_timestamp' in df.columns and 'price' in df.columns:
        df_valid = df.dropna(subset=['order_purchase_timestamp'])
        monthly = df_valid.groupby(
            df_valid['order_purchase_timestamp'].dt.to_period('M')
        )['price'].sum()

        ax.plot(monthly.index.astype(str), monthly.values,
                marker='o', linewidth=2, markersize=6, color='#2E86AB')
    else:
        ax.text(0.5, 0.5, 'No revenue data available', transform=ax.transAxes, ha='center')

    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Revenue ($)', fontsize=12)
    ax.set_title('Monthly Revenue Trend', fontsize=14, fontweight='bold')
    ax.tick_params(axis='x', rotation=45)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

    plt.tight_layout()

    # Ensure output directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

    return save_path


def plot_top_categories(df: pd.DataFrame, save_path: str,
                        top_n: int = 10) -> str:
    """
    Create bar chart showing top-selling product categories.

    Args:
        df: DataFrame with product_category_name_english and price columns
        save_path: Path to save the chart image
        top_n: Number of top categories to display

    Returns:
        Path to saved chart
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    if 'product_category_name_english' in df.columns and 'price' in df.columns:
        category_revenue = df.groupby('product_category_name_english')['price'].sum()
        top_categories = category_revenue.nlargest(top_n)

        colors = sns.color_palette("viridis", len(top_categories))
        bars = ax.barh(range(len(top_categories)), top_categories.values, color=colors)

        ax.set_yticks(range(len(top_categories)))
        ax.set_yticklabels([cat.replace('_', ' ').title() for cat in top_categories.index])
        ax.set_xlabel('Revenue ($)', fontsize=12)
        ax.set_title(f'Top {top_n} Product Categories by Revenue', fontsize=14, fontweight='bold')

        # Add value labels on bars
        for bar, value in zip(bars, top_categories.values):
            ax.text(bar.get_width() + top_categories.max() * 0.01,
                    bar.get_y() + bar.get_height() / 2,
                    f'${value:,.0f}', va='center', fontsize=9)
    else:
        ax.text(0.5, 0.5, 'No category data available', transform=ax.transAxes, ha='center')

    ax.invert_yaxis()
    plt.tight_layout()

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

    return save_path


def plot_payment_types(df: pd.DataFrame, save_path: str) -> str:
    """
    Create pie chart showing payment type distribution.

    Args:
        df: DataFrame with payment_type column
        save_path: Path to save the chart image

    Returns:
        Path to saved chart
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    if 'payment_type' in df.columns:
        payment_counts = df['payment_type'].value_counts()

        # Pie chart - count distribution
        colors = sns.color_palette("Set2", len(payment_counts))
        wedges, texts, autotexts = axes[0].pie(
            payment_counts.values,
            labels=[pt.replace('_', ' ').title() for pt in payment_counts.index],
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )

        # Enhance text visibility
        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')

        axes[0].set_title('Payment Method Distribution (by Count)', fontsize=14, fontweight='bold')

        # Bar chart - value distribution
        if 'payment_value' in df.columns:
            payment_values = df.groupby('payment_type')['payment_value'].sum()
            bars = axes[1].bar(
                [pt.replace('_', ' ').title() for pt in payment_values.index],
                payment_values.values,
                color=sns.color_palette("coolwarm", len(payment_values))
            )

            axes[1].set_xlabel('Payment Type', fontsize=12)
            axes[1].set_ylabel('Total Value ($)', fontsize=12)
            axes[1].set_title('Payment Value by Method', fontsize=14, fontweight='bold')
            axes[1].tick_params(axis='x', rotation=45)
            axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        else:
            axes[1].text(0.5, 0.5, 'No payment value data', transform=axes[1].transAxes, ha='center')
    else:
        axes[0].text(0.5, 0.5, 'No payment data available', transform=axes[0].transAxes, ha='center')
        axes[1].text(0.5, 0.5, '', transform=axes[1].transAxes)

    plt.tight_layout()

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

    return save_path


def plot_correlation_heatmap(df: pd.DataFrame, save_path: str) -> str:
    """
    Create heatmap showing correlations between numerical features.

    Args:
        df: DataFrame with numerical columns
        save_path: Path to save the chart image

    Returns:
        Path to saved chart
    """
    fig, ax = plt.subplots(figsize=(12, 10))

    # Select numerical columns for correlation
    numeric_cols = ['price', 'payment_value', 'payment_installments',
                    'review_score', 'product_weight_lg', 'freight_value']

    available_cols = [col for col in numeric_cols if col in df.columns]

    if len(available_cols) >= 2:
        corr_matrix = df[available_cols].corr()

        # Create heatmap with diverging colormap
        mask = pd.DataFrame(0, index=corr_matrix.index, columns=corr_matrix.columns)
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                    square=True, linewidths=1, cbar_kws={'shrink': 0.8},
                    ax=ax, vmin=-1, vmax=1)

        ax.set_title('Feature Correlation Heatmap', fontsize=14, fontweight='bold')
    else:
        ax.text(0.5, 0.5, 'Insufficient numerical data for correlation analysis',
                transform=ax.transAxes, ha='center')

    plt.tight_layout()

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

    return save_path


def plot_delivery_histogram(df: pd.DataFrame, save_path: str) -> str:
    """
    Create histogram showing delivery time distribution.

    Args:
        df: DataFrame with order_purchase_timestamp and order_delivered_customer_date
        save_path: Path to save the chart image

    Returns:
        Path to saved chart
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Calculate delivery times
    if 'order_purchase_timestamp' in df.columns and 'order_delivered_customer_date' in df.columns:
        df_copy = df.copy()
        df_copy['delivery_time'] = (
            df_copy['order_delivered_customer_date'] - df_copy['order_purchase_timestamp']
        ).dt.days

        # Filter valid delivery times (0-60 days)
        valid_delivery = df_copy[
            (df_copy['delivery_time'] >= 0) &
            (df_copy['delivery_time'] <= 60) &
            (df_copy['delivery_time'].notna())
        ]

        if len(valid_delivery) > 0:
            delivery_times = valid_delivery['delivery_time']

            # Create histogram with KDE
            sns.histplot(data=valid_delivery, x='delivery_time', ax=ax,
                         kde=True, color='#28A745', bins=30)

            # Add vertical lines for mean and median
            mean_time = delivery_times.mean()
            median_time = delivery_times.median()

            ax.axvline(mean_time, color='red', linestyle='--', linewidth=2,
                       label=f'Mean: {mean_time:.1f} days')
            ax.axvline(median_time, color='blue', linestyle='--', linewidth=2,
                       label=f'Median: {median_time:.1f} days')

            ax.set_xlabel('Delivery Time (days)', fontsize=12)
            ax.set_ylabel('Number of Orders', fontsize=12)
            ax.set_title('Delivery Time Distribution', fontsize=14, fontweight='bold')
            ax.legend()
        else:
            ax.text(0.5, 0.5, 'No valid delivery data available', transform=ax.transAxes, ha='center')
    else:
        ax.text(0.5, 0.5, 'No delivery timestamp data available', transform=ax.transAxes, ha='center')

    plt.tight_layout()

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

    return save_path


def plot_customer_geography(df: pd.DataFrame, save_path: str) -> str:
    """
    Create bar chart showing customer distribution by state.

    Args:
        df: DataFrame with customer_state column
        save_path: Path to save the chart image

    Returns:
        Path to saved chart
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    if 'customer_state' in df.columns:
        state_counts = df['customer_state'].value_counts().head(15)

        colors = sns.color_palette("mako", len(state_counts))
        bars = ax.bar(state_counts.index, state_counts.values, color=colors)

        ax.set_xlabel('State', fontsize=12)
        ax.set_ylabel('Number of Customers', fontsize=12)
        ax.set_title('Top 15 States by Customer Count', fontsize=14, fontweight='bold')
        ax.tick_params(axis='x', rotation=45)

        # Add value labels
        for bar, count in zip(bars, state_counts.values):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + state_counts.max() * 0.01,
                    f'{count:,}', ha='center', fontsize=9)
    else:
        ax.text(0.5, 0.5, 'No state data available', transform=ax.transAxes, ha='center')

    plt.tight_layout()

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

    return save_path


def save_all_charts(df: pd.DataFrame, output_dir: str,
                    analysis_results: Optional[dict] = None) -> dict:
    """
    Generate and save all visualization charts.

    Args:
        df: Merged DataFrame
        output_dir: Directory to save chart images
        analysis_results: Pre-computed analysis results (optional)

    Returns:
        Dictionary mapping chart names to saved file paths
    """
    os.makedirs(output_dir, exist_ok=True)

    saved_charts = {}

    print("Generating revenue trend chart...")
    monthly_data = analysis_results.get('sales', {}).get('monthly_revenue') if analysis_results else None
    saved_charts['revenue_trend'] = plot_revenue_trend(
        df, os.path.join(output_dir, 'revenue_trend.png'), monthly_data
    )

    print("Generating top categories chart...")
    saved_charts['top_categories'] = plot_top_categories(
        df, os.path.join(output_dir, 'top_categories.png')
    )

    print("Generating payment types chart...")
    saved_charts['payment_types'] = plot_payment_types(
        df, os.path.join(output_dir, 'payment_types.png')
    )

    print("Generating correlation heatmap...")
    saved_charts['correlation_heatmap'] = plot_correlation_heatmap(
        df, os.path.join(output_dir, 'correlation_heatmap.png')
    )

    print("Generating delivery time histogram...")
    saved_charts['delivery_times'] = plot_delivery_histogram(
        df, os.path.join(output_dir, 'delivery_times.png')
    )

    print("Generating customer geography chart...")
    saved_charts['customer_geography'] = plot_customer_geography(
        df, os.path.join(output_dir, 'customer_geography.png')
    )

    print(f"\nSaved {len(saved_charts)} charts to {output_dir}")
    return saved_charts
