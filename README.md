# E-commerce Sales Analysis

A comprehensive data analytics project analyzing the Brazilian E-Commerce Public Dataset by Olist to extract actionable business insights.

## Project Overview

This project analyzes e-commerce data to provide insights on:
- **Sales Performance** - Revenue trends, top categories
- **Customer Behavior** - Geographic distribution, repeat customers
- **Delivery Efficiency** - Delivery times, delays, impact on reviews
- **Product Trends** - Most sold products, category performance
- **Payment Analysis** - Payment methods, installment usage

## Dataset

[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

The dataset contains real e-commerce transactions from Olist, a Brazilian marketplace.

## Project Structure

```
Ecommerce_Sales_Analysis/
├── data/                    # Raw CSV files from dataset
├── notebooks/
│   └── analysis.ipynb       # Interactive analysis notebook
├── src/
│   ├── __init__.py          # Package initialization
│   ├── data_cleaning.py     # Data loading and cleaning
│   ├── analysis.py          # Business analysis functions
│   └── visualization.py     # Chart generation
├── outputs/
│   ├── charts/              # Saved visualization images
│   └── reports/             # Generated reports
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Setup Instructions

### 1. Clone or Download the Project

Navigate to the project directory:
```bash
cd Ecommerce_Sales_Analysis
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download the Dataset

1. Go to [Kaggle Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
2. Download the dataset ZIP file
3. Extract all CSV files into the `data/` folder

Required files:
- `olist_orders_dataset.csv`
- `olist_customers_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_products_dataset.csv`
- `olist_sellers_dataset.csv`
- `olist_products_category_name_translation.csv`

### 4. Run the Analysis

#### Option A: Jupyter Notebook (Recommended)

```bash
jupyter notebook
```

Then open `notebooks/analysis.ipynb` and run all cells.

#### Option B: Python Scripts

```python
from src.data_cleaning import load_data, clean_data, merge_data
from src.analysis import generate_full_analysis
from src.visualization import save_all_charts

# Load and process data
raw_data = load_data('data/')
cleaned = clean_data(raw_data)
df = merge_data(cleaned)

# Run analysis and save outputs
results = generate_full_analysis(df)
save_all_charts(df, 'outputs/charts/')
```

## Output Files

After running the analysis, you'll find:

### Charts (`outputs/charts/`)
- `revenue_trend.png` - Monthly revenue trend line chart
- `top_categories.png` - Top-selling product categories bar chart
- `payment_types.png` - Payment method distribution pie chart
- `correlation_heatmap.png` - Feature correlation heatmap
- `delivery_times.png` - Delivery time distribution histogram

### Reports (`outputs/reports/`)
- `summary.txt` - Comprehensive business insights report

## Key Metrics Analyzed

| Category | Metrics |
|----------|---------|
| Sales | Total revenue, monthly trends, category performance |
| Customers | Unique customers, repeat rate, geographic distribution |
| Products | Most sold items, category rankings |
| Delivery | Average delivery time, delay rate, review correlation |
| Payments | Payment type distribution, average installments |

## Requirements

- Python 3.9+
- pandas
- numpy
- matplotlib
- seaborn
- plotly (optional, for interactive charts)
- jupyter

## License

This project is for educational and analytical purposes. The dataset is subject to [Kaggle's terms of service](https://www.kaggle.com/terms).

## Author

Built as a comprehensive data analytics demonstration project.
