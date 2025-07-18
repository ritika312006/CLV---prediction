import streamlit as st
import pandas as pd
import chardet
import io
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="CLV Prediction", layout="wide")
st.title(" Customer lifetime value (CLV) - Prediction ")

st.markdown("Upload your sales data CSV to visualize trends and explore customer value insights.")

# --- File Upload ---
uploaded = st.file_uploader("📁 Upload CSV File", type=["csv"])

if uploaded:
    # --- Encoding Detection ---
    raw_bytes = uploaded.read()
    raw_sample = raw_bytes[:100000]
    detected_encoding = chardet.detect(raw_sample)['encoding']

    if detected_encoding is None or detected_encoding.lower() == "ascii":
        encoding_used = "ISO-8859-1"
    else:
        encoding_used = detected_encoding

    st.caption(f"✅ Detected Encoding: `{encoding_used}`")

    try:
        bio = io.BytesIO(raw_bytes)
        df = pd.read_csv(
            bio,
            encoding=encoding_used,
            names=['invoice', 'stockcode', 'description', 'quantity', 'invoicedate',
                   'unitprice', 'customerid', 'country'],
            header=0,
            parse_dates=['invoicedate']
        )

        # --- Clean & Prepare ---
        df['invoicedate'] = pd.to_datetime(df['invoicedate'], errors='coerce')
        df = df.dropna(subset=['invoicedate', 'quantity', 'unitprice'])
        df['profit'] = df['quantity'] * df['unitprice'] * 0.2

        st.success("✅ File loaded successfully!")

        # --- Filters ---
        st.subheader("🔍 Filter Data")
        col1, col2 = st.columns(2)
        search_text = col1.text_input("Search Description")
        countries = df['country'].dropna().unique().tolist()
        selected_country = col2.selectbox("Select Country", options=["All"] + sorted(countries))

        filtered_df = df.copy()
        if search_text:
            filtered_df = filtered_df[filtered_df['description'].str.contains(search_text, case=False, na=False)]
        if selected_country != "All":
            filtered_df = filtered_df[filtered_df['country'] == selected_country]

        # --- KPIs ---
        st.subheader("📊 Key Metrics")
        total_sales = (filtered_df['quantity'] * filtered_df['unitprice']).sum()
        total_profit = filtered_df['profit'].sum()
        date_min = filtered_df['invoicedate'].min()
        date_max = filtered_df['invoicedate'].max()

        k1, k2, k3 = st.columns(3)
        k1.metric("🛒 Total Sales", f"${total_sales:,.2f}")
        k2.metric("💰 Total Profit", f"${total_profit:,.2f}")
        k3.metric("📅 Date Range", f"{date_min.date()} → {date_max.date()}")

        # --- Download Filtered Data ---
        st.download_button("⬇️ Download Filtered Data as CSV", data=filtered_df.to_csv(index=False),
                           file_name="filtered_sales.csv", mime="text/csv")

        # --- Data Table ---
        st.subheader("📄 Data Preview")
        st.dataframe(filtered_df.head(20), use_container_width=True)

        # --- Sales Over Time ---
        st.subheader("📈 Sales Over Time")
        sales_over_time = filtered_df.groupby('invoicedate').apply(lambda x: (x['quantity'] * x['unitprice']).sum())
        st.line_chart(sales_over_time)

        # --- Monthly Trend ---
        st.subheader("📆 Monthly Sales Trend")
        monthly_sales = filtered_df.resample('M', on='invoicedate').apply(lambda x: (x['quantity'] * x['unitprice']).sum())
        st.line_chart(monthly_sales)

        # --- CLV Chart: Top Customers ---
        st.subheader("👤 Top 10 Customers by Total Spend")
        clv = filtered_df.groupby('customerid').apply(lambda x: (x['quantity'] * x['unitprice']).sum())
        clv = clv.sort_values(ascending=False).head(10)
        st.bar_chart(clv)

        # --- Pie Chart: Orders by Country ---
        st.subheader("🌍 Orders Distribution by Country")
        order_dist = filtered_df['country'].value_counts()
        fig = px.pie(values=order_dist.values, names=order_dist.index, title="Orders by Country")
        st.plotly_chart(fig)

        st.markdown("---")
        st.caption("Built for CLV Prediction — Simple, Reusable, and Insightful.")

    except Exception as e:
        st.error(f"❌ Failed to load CSV: {e}")
else:
    st.info("Upload a CSV file to begin.")

# --- Add Use Cases and About section ---
st.markdown("---")
with st.expander("💡 Use Cases: How This Dashboard Helps"):
    st.markdown("""
    - 📊 **Track sales performance** over time to identify seasonal trends.
    - 👤 **Discover high-value customers** by calculating total spending.
    - 🌍 **Understand geographic demand** using country-wise sales insights.
    - 💰 **Optimize marketing spend** by focusing on top-performing customers.
    """)

with st.expander("📘 About This Project"):
    st.markdown("""
    This project was created as part of my internship to demonstrate how businesses can analyze transactional sales data
    to make smarter decisions using Customer Lifetime Value (CLV) principles.

    **Built With:**
    - Python 🐍
    - Streamlit 📈
    - Pandas + Plotly for interactive charts

    **Made by:** *[Ritika Bagoria]*  
    [GitHub Repo](https://github.com/your-username/clv-dashboard)  
    """)
