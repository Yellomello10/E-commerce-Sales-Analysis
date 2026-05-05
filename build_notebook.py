"""Generate the full analysis notebook for the Olist Brazilian E-Commerce dataset."""
import json, os

def md(src): return {"cell_type":"markdown","metadata":{},"source":[src]}
def code(lines): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":lines}

cells = []

# ── Part 1: Setup ─────────────────────────────────────────────────────────────
cells.append(md("# E-commerce Sales Analysis\n## Brazilian E-Commerce Public Dataset by Olist (Full Kaggle Dataset)\n\nAll 9 tables from `kagglehub`. Run cells top to bottom.\n"))
cells.append(md("## Part 1: Setup"))
cells.append(code("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.append(os.path.join(os.getcwd(), ".."))

from src.data_cleaning import load_data, clean_data, merge_data
from src.analysis import analyze_sales, analyze_customers, analyze_products, analyze_delivery, analyze_payments
from src.kpi_dashboard import calculate_kpis, generate_kpi_summary, get_kpi_alerts, create_kpi_scorecard
from src.advanced_insights import (perform_rfm_segmentation, calculate_customer_lifetime_value,
                                   forecast_sales, calculate_churn_risk, perform_cohort_analysis)
from src.visualization import save_all_charts
from src.interactive_dashboard import create_full_dashboard
from src.executive_report import generate_executive_summary, save_executive_report

pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", "{:.2f}".format)
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")
print("Libraries loaded OK")
""".splitlines(keepends=True)))

# ── Part 2: Load ──────────────────────────────────────────────────────────────
cells.append(md("## Part 2: Data Loading & Cleaning"))
cells.append(code("""DATA_DIR   = "../data"
OUTPUT_DIR = "../outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

raw_data = load_data(DATA_DIR)
cleaned  = clean_data(raw_data)
df       = merge_data(cleaned)
print(f"Merged shape: {df.shape}")
""".splitlines(keepends=True)))

cells.append(code("""for name, dframe in cleaned.items():
    if dframe is not None:
        print(f"{name:<25s} {dframe.shape[0]:>9,} rows x {dframe.shape[1]:>2} cols")
""".splitlines(keepends=True)))

cells.append(code("df.head(3)\n".splitlines(keepends=True)))

# ── Part 3: KPIs ──────────────────────────────────────────────────────────────
cells.append(md("## Part 3: KPI Dashboard"))
cells.append(code("""kpis = calculate_kpis(df)
print(generate_kpi_summary(kpis))
""".splitlines(keepends=True)))

cells.append(code("""alerts = get_kpi_alerts(kpis)
if alerts:
    for a in alerts:
        icon = "[!!]" if a["severity"] == "HIGH" else "[!]"
        print(f"{icon} {a['severity']}: {a['message']}")
else:
    print("All KPIs within healthy ranges.")
""".splitlines(keepends=True)))

cells.append(code("create_kpi_scorecard(kpis)\n".splitlines(keepends=True)))

# ── Part 4: Sales ─────────────────────────────────────────────────────────────
cells.append(md("## Part 4: Sales Analysis"))
cells.append(code("""sales = analyze_sales(df)
print(f"Total Revenue   : R${sales['total_revenue']:>15,.2f}")
print(f"Total Orders    : {sales['total_orders']:>15,}")
print(f"Avg Order Value : R${sales['avg_order_value']:>15.2f}")
""".splitlines(keepends=True)))

cells.append(code("""monthly = sales["monthly_revenue"]
if not monthly.empty:
    fig, ax = plt.subplots(figsize=(14, 5))
    x = range(len(monthly))
    ax.plot(x, monthly["revenue"], marker="o", lw=2, color="#2E86AB")
    ax.fill_between(x, monthly["revenue"], alpha=0.15, color="#2E86AB")
    ax.set_xticks(x)
    ax.set_xticklabels(monthly["month"].astype(str), rotation=45, ha="right")
    ax.set_title("Monthly Revenue Trend", fontsize=14, fontweight="bold")
    ax.set_ylabel("Revenue (R$)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"R${v:,.0f}"))
    plt.tight_layout(); plt.show()
""".splitlines(keepends=True)))

cells.append(code("""top_cats = sales["top_categories"]
if not top_cats.empty:
    fig, ax = plt.subplots(figsize=(12, 7))
    labels = top_cats["category"].str.replace("_", " ").str.title()
    ax.barh(labels, top_cats["revenue"], color=sns.color_palette("viridis", len(top_cats)))
    ax.invert_yaxis()
    ax.set_title("Top 10 Categories by Revenue", fontsize=14, fontweight="bold")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"R${v:,.0f}"))
    plt.tight_layout(); plt.show()
""".splitlines(keepends=True)))

cells.append(md("### Weekly Order Heatmap (Day × Hour)"))
cells.append(code("""tmp = df.dropna(subset=["order_purchase_timestamp"]).copy()
tmp["dow"]  = tmp["order_purchase_timestamp"].dt.day_name()
tmp["hour"] = tmp["order_purchase_timestamp"].dt.hour
pivot = tmp.groupby(["dow", "hour"])["order_id"].nunique().unstack(fill_value=0)
day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
pivot = pivot.reindex([d for d in day_order if d in pivot.index])
fig, ax = plt.subplots(figsize=(16, 5))
sns.heatmap(pivot, cmap="YlOrRd", ax=ax, linewidths=0.3)
ax.set_title("Orders by Day of Week and Hour", fontsize=14, fontweight="bold")
ax.set_xlabel("Hour of Day"); ax.set_ylabel("")
plt.tight_layout(); plt.show()
""".splitlines(keepends=True)))

# ── Part 5: Customers ─────────────────────────────────────────────────────────
cells.append(md("## Part 5: Customer Analysis"))
cells.append(code("""customer_results = analyze_customers(df)
print(f"Unique Customers : {customer_results['unique_customers']:,}")
print(f"Repeat Customers : {customer_results['repeat_customers']:,}")
print(f"Repeat Rate      : {customer_results['repeat_rate']*100:.1f}%")
""".splitlines(keepends=True)))

cells.append(code("""fig, axes = plt.subplots(1, 2, figsize=(14, 5))
ts = customer_results["top_states"]
axes[0].bar(ts["state"], ts["revenue"],
            color=sns.color_palette("coolwarm", len(ts)))
axes[0].set_title("Revenue by State", fontweight="bold")
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"R${v:,.0f}"))
axes[0].tick_params(axis="x", rotation=45)

tc = customer_results["top_cities"]
axes[1].barh(tc["city"], tc["customers"],
             color=sns.color_palette("mako", len(tc)))
axes[1].invert_yaxis()
axes[1].set_title("Top Cities by Customer Count", fontweight="bold")
plt.tight_layout(); plt.show()
""".splitlines(keepends=True)))

# ── Part 6: Reviews ───────────────────────────────────────────────────────────
cells.append(md("## Part 6: Review Score Analysis"))
cells.append(code("""if "review_score" in df.columns:
    colors5 = ["#d62728","#ff7f0e","#ffbb78","#98df8a","#2ca02c"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    rc = df["review_score"].value_counts().sort_index()
    axes[0].bar(rc.index.astype(int), rc.values, color=colors5)
    axes[0].set_title("Review Score Distribution", fontweight="bold")
    axes[0].set_xlabel("Score"); axes[0].set_ylabel("Count")

    df_rv = df.copy()
    df_rv["delivery_time"] = (df_rv["order_delivered_customer_date"] -
                              df_rv["order_purchase_timestamp"]).dt.days
    sd = df_rv.groupby("review_score")["delivery_time"].mean()
    axes[1].bar(sd.index.astype(int), sd.values, color=colors5)
    axes[1].set_title("Avg Delivery Time by Review Score", fontweight="bold")
    axes[1].set_xlabel("Score"); axes[1].set_ylabel("Days")

    plt.tight_layout(); plt.show()
    avg = df["review_score"].mean()
    pos = (df["review_score"] >= 4).mean() * 100
    print(f"Avg Score: {avg:.2f}/5  |  Positive (>=4): {pos:.1f}%")
""".splitlines(keepends=True)))

# ── Part 7: Sellers ───────────────────────────────────────────────────────────
cells.append(md("## Part 7: Seller Analysis"))
cells.append(code("""if "seller_id" in df.columns:
    seller_perf = (df.groupby("seller_id")
                   .agg(orders=("order_id", "nunique"),
                        revenue=("price", "sum"),
                        avg_score=("review_score", "mean"))
                   .sort_values("revenue", ascending=False))
    print(f"Total Sellers: {len(seller_perf):,}")
    top10pct = max(1, int(len(seller_perf) * 0.1))
    top_rev  = seller_perf["revenue"].nlargest(top10pct).sum()
    total_rv = seller_perf["revenue"].sum()
    print(f"Top 10% sellers account for {top_rev/total_rv*100:.1f}% of revenue")
    display(seller_perf.head(10))
""".splitlines(keepends=True)))

cells.append(code("""if "seller_id" in df.columns:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].hist(seller_perf["orders"], bins=40, color="#5B84B1", edgecolor="white")
    axes[0].set_title("Seller Order Volume Distribution", fontweight="bold")
    axes[0].set_xlabel("Orders per Seller"); axes[0].set_ylabel("Sellers")

    axes[1].hist(seller_perf["avg_score"].dropna(), bins=20, color="#E67E22", edgecolor="white")
    axes[1].set_title("Seller Avg Review Score Distribution", fontweight="bold")
    axes[1].set_xlabel("Avg Review Score"); axes[1].set_ylabel("Sellers")
    plt.tight_layout(); plt.show()
""".splitlines(keepends=True)))

# ── Part 8: Delivery ──────────────────────────────────────────────────────────
cells.append(md("## Part 8: Delivery Analysis"))
cells.append(code("""delivery_results = analyze_delivery(df)
print(f"Avg Delivery Time    : {delivery_results['avg_delivery_time']:.1f} days")
print(f"Median               : {delivery_results['median_delivery_time']:.1f} days")
print(f"Delay Rate           : {delivery_results['delay_rate']*100:.1f}%")
print(f"Delivery-Review Corr : {delivery_results['delivery_review_correlation']:.3f}")
""".splitlines(keepends=True)))

cells.append(code("""dt = delivery_results["delivery_times"]
if len(dt) > 0:
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.histplot(dt, kde=True, bins=40, color="#28A745", ax=ax)
    ax.axvline(delivery_results["avg_delivery_time"],    color="red",  ls="--", lw=2,
               label=f"Mean {delivery_results['avg_delivery_time']:.1f}d")
    ax.axvline(delivery_results["median_delivery_time"], color="blue", ls="--", lw=2,
               label=f"Median {delivery_results['median_delivery_time']:.1f}d")
    ax.set_title("Delivery Time Distribution", fontweight="bold")
    ax.set_xlabel("Days"); ax.legend()
    plt.tight_layout(); plt.show()
""".splitlines(keepends=True)))

cells.append(md("### Delivery Time by State"))
cells.append(code("""df_del = df.copy()
df_del["delivery_time"] = (df_del["order_delivered_customer_date"] -
                           df_del["order_purchase_timestamp"]).dt.days
state_del = df_del.groupby("customer_state")["delivery_time"].mean().sort_values(ascending=False).head(15)
fig, ax = plt.subplots(figsize=(12, 5))
ax.bar(state_del.index, state_del.values, color=sns.color_palette("rocket", len(state_del)))
ax.set_title("Avg Delivery Time by State (Top 15 Slowest)", fontweight="bold")
ax.set_ylabel("Days")
plt.tight_layout(); plt.show()
""".splitlines(keepends=True)))

# ── Part 9: Payments ──────────────────────────────────────────────────────────
cells.append(md("## Part 9: Payment Analysis"))
cells.append(code("""payment_results = analyze_payments(df)
print(f"Avg Installments : {payment_results['avg_installments']:.1f}")
print(f"Installment Rate : {payment_results['installment_rate']*100:.1f}%")
display(payment_results["payment_type_distribution"])
""".splitlines(keepends=True)))

cells.append(code("""if "payment_type" in df.columns:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    pc = df["payment_type"].value_counts()
    axes[0].pie(pc.values,
                labels=[x.replace("_", " ").title() for x in pc.index],
                autopct="%1.1f%%", startangle=90,
                colors=sns.color_palette("Set2", len(pc)))
    axes[0].set_title("Payment Method Distribution", fontweight="bold")

    cc = df[df["payment_type"] == "credit_card"]["payment_installments"].value_counts().sort_index()
    axes[1].bar(cc.index, cc.values, color="#5B84B1")
    axes[1].set_title("Credit Card Installments", fontweight="bold")
    axes[1].set_xlabel("Installments"); axes[1].set_ylabel("Orders")
    plt.tight_layout(); plt.show()
""".splitlines(keepends=True)))

# ── Part 10: Products ─────────────────────────────────────────────────────────
cells.append(md("## Part 10: Product Analysis"))
cells.append(code("""product_results = analyze_products(df)
display(product_results["category_by_quantity"].head(10))
""".splitlines(keepends=True)))

cells.append(code("""apc = product_results["avg_price_by_category"]
if not apc.empty:
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh(apc["category"].str.replace("_", " ").str.title(), apc["avg_price"],
            color=sns.color_palette("plasma", len(apc)))
    ax.invert_yaxis()
    ax.set_title("Top 10 Categories by Avg Price", fontweight="bold")
    ax.set_xlabel("Avg Price (R$)")
    plt.tight_layout(); plt.show()
""".splitlines(keepends=True)))

# ── Part 11: RFM ──────────────────────────────────────────────────────────────
cells.append(md("## Part 11: RFM Customer Segmentation"))
cells.append(code("""rfm = perform_rfm_segmentation(df)
if not rfm.empty:
    seg = rfm["segment"].value_counts()
    for s, n in seg.items():
        print(f"  {s:<20s} {n:6,}  ({n/len(rfm)*100:.1f}%)")
""".splitlines(keepends=True)))

cells.append(code("""if not rfm.empty:
    seg = rfm["segment"].value_counts()
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    colors = sns.color_palette("Set3", len(seg))
    axes[0].bar(seg.index, seg.values, color=colors)
    axes[0].set_title("Customer Segments (RFM)", fontweight="bold")
    axes[0].tick_params(axis="x", rotation=45)

    sm = rfm.groupby("segment")["monetary"].mean().sort_values(ascending=False)
    axes[1].barh(sm.index, sm.values, color=sns.color_palette("viridis", len(sm)))
    axes[1].invert_yaxis()
    axes[1].set_title("Avg Spend per Segment", fontweight="bold")
    axes[1].set_xlabel("Avg Monetary (R$)")
    plt.tight_layout(); plt.show()
""".splitlines(keepends=True)))

# ── Part 12: Cohort ───────────────────────────────────────────────────────────
cells.append(md("## Part 12: Cohort Retention Analysis"))
cells.append(code("""cohort = perform_cohort_analysis(df)
ret = cohort.get("retention_matrix")
if ret is not None and not ret.empty:
    ret_plot = ret.iloc[:12, :7].fillna(0)
    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(ret_plot, annot=True, fmt=".0f", cmap="YlGnBu",
                linewidths=0.5, ax=ax, vmin=0, vmax=100,
                cbar_kws={"label": "Retention %"})
    ax.set_title("Customer Cohort Retention Matrix (%)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Period Number (Months After First Purchase)")
    ax.set_ylabel("Cohort (First Purchase Month)")
    plt.tight_layout(); plt.show()
else:
    print("Cohort data unavailable — need customers with multiple orders.")
""".splitlines(keepends=True)))

# ── Part 13: CLV ─────────────────────────────────────────────────────────────
cells.append(md("## Part 13: Customer Lifetime Value"))
cells.append(code("""clv = calculate_customer_lifetime_value(df, months_ahead=12)
if not clv.empty:
    p = clv["predicted_clv"]
    print(f"Avg CLV (12 mo)  : R${p.mean():,.2f}")
    print(f"Median CLV       : R${p.median():,.2f}")
    print(f"Top 1% threshold : R${p.quantile(0.99):,.2f}")
    clv_cap = p.clip(upper=p.quantile(0.95))
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(clv_cap, bins=40, kde=True, color="#9B59B6", ax=ax)
    ax.set_title("Predicted CLV Distribution (capped at 95th pct)", fontweight="bold")
    ax.set_xlabel("Predicted 12-Month CLV (R$)")
    plt.tight_layout(); plt.show()
""".splitlines(keepends=True)))

# ── Part 14: Churn ────────────────────────────────────────────────────────────
cells.append(md("## Part 14: Churn Risk Analysis"))
cells.append(code("""churn = calculate_churn_risk(df, days_threshold=90)
if not churn.empty:
    cr = churn["churn_risk"].value_counts()
    for risk, count in cr.items():
        print(f"  {risk:<10s} Risk: {count:7,}  ({count/len(churn)*100:.1f}%)")
    order   = ["Very Low", "Low", "Medium", "High"]
    vals    = [cr.get(o, 0) for o in order]
    clrs    = ["#2ecc71", "#f1c40f", "#e67e22", "#e74c3c"]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(order, vals, color=clrs)
    ax.set_title("Churn Risk Distribution", fontweight="bold")
    ax.set_ylabel("Customers")
    plt.tight_layout(); plt.show()
""".splitlines(keepends=True)))

# ── Part 15: Forecast ─────────────────────────────────────────────────────────
cells.append(md("## Part 15: Sales Forecast (3 Months)"))
cells.append(code("""forecast = forecast_sales(df, periods=3)
hist = forecast[~forecast["is_forecast"]]
pred = forecast[forecast["is_forecast"]]
all_months = list(hist["month"].astype(str)) + list(pred["month"].astype(str))
all_sales  = list(hist["sales"]) + list(pred["sales"])
x_h = range(len(hist))
x_p = range(len(hist) - 1, len(hist) + len(pred) - 1)

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(x_h, hist["sales"].values, marker="o", lw=2, label="Historical", color="#2E86AB")
ax.plot(x_p, [hist["sales"].values[-1]] + list(pred["sales"].values),
        marker="s", lw=2, ls="--", label="Forecasted", color="#DC3545")
ax.set_xticks(range(len(all_months)))
ax.set_xticklabels(all_months, rotation=45, ha="right")
ax.set_title("Sales Forecast", fontsize=14, fontweight="bold")
ax.set_ylabel("Revenue (R$)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"R${v:,.0f}"))
ax.legend(); plt.tight_layout(); plt.show()
print("Forecasted revenue:")
for _, r in pred.iterrows():
    print(f"  {r['month']}: R${r['sales']:,.2f}")
""".splitlines(keepends=True)))

# ── Part 16: Correlation ──────────────────────────────────────────────────────
cells.append(md("## Part 16: Feature Correlation Heatmap"))
cells.append(code("""num_cols = [c for c in ["price","freight_value","payment_value",
                            "payment_installments","review_score"]
            if c in df.columns]
if len(num_cols) >= 2:
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(df[num_cols].corr(), annot=True, fmt=".2f", cmap="RdBu_r",
                center=0, square=True, linewidths=1, ax=ax, vmin=-1, vmax=1)
    ax.set_title("Feature Correlation Heatmap", fontweight="bold")
    plt.tight_layout(); plt.show()
""".splitlines(keepends=True)))

# ── Part 17: Reports ──────────────────────────────────────────────────────────
cells.append(md("## Part 17: Executive Summary & Reports"))
cells.append(code("""reports_dir = os.path.join(OUTPUT_DIR, "reports")
os.makedirs(reports_dir, exist_ok=True)
exec_path = os.path.join(reports_dir, "executive_summary.txt")
save_executive_report(df, exec_path)
print(generate_executive_summary(df, kpis))
""".splitlines(keepends=True)))

# ── Part 18: Static Charts ────────────────────────────────────────────────────
cells.append(md("## Part 18: Save Static Charts"))
cells.append(code("""all_results = {
    "sales":     sales,
    "customers": customer_results,
    "products":  product_results,
    "delivery":  delivery_results,
    "payments":  payment_results
}
charts_dir  = os.path.join(OUTPUT_DIR, "charts")
saved_charts = save_all_charts(df, charts_dir, all_results)
print(f"Saved {len(saved_charts)} charts to {charts_dir}")
""".splitlines(keepends=True)))

# ── Part 19: Dashboards ───────────────────────────────────────────────────────
cells.append(md("## Part 19: Interactive Dashboards"))
cells.append(code("""dashboard_dir = os.path.join(OUTPUT_DIR, "dashboards")
saved_dashboards = create_full_dashboard(df, kpis, dashboard_dir)
for name, path in saved_dashboards.items():
    print(f"  {name}: {path}")
print("Open any HTML file in a browser to view!")
""".splitlines(keepends=True)))

cells.append(md("---\n## Analysis Complete!\n\nAll outputs saved to `outputs/`. Open HTML dashboards in a browser for interactive exploration.\n"))

# ── Build and write ───────────────────────────────────────────────────────────
nb = {
    "nbformat": 4,
    "nbformat_minor": 4,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.9.0"}
    },
    "cells": cells
}

out = os.path.join(os.path.dirname(__file__), "notebooks", "analysis.ipynb")
with open(out, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)
print(f"Written {len(cells)} cells -> {out}")
