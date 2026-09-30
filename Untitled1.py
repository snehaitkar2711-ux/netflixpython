import base64
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Netflix Insights",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).resolve().parent / "netflix.csv"
LOGO_PATH = Path(__file__).resolve().parent / "logo.jpg"
BACKGROUND_PATH = Path(__file__).resolve().parent / "bg.png"
REQUIRED_COLUMNS = {
    "Customer_ID",
    "Region",
    "Subscription_Plan",
    "Category",
    "Rating",
    "Watch_Date",
    "Watch_Time_Minutes",
    "Monthly_Revenue",
}
ACCENT = "#E50914"


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    missing_columns = REQUIRED_COLUMNS.difference(data.columns)
    if missing_columns:
        raise ValueError(
            "The CSV is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    data["Watch_Date"] = pd.to_datetime(data["Watch_Date"], errors="coerce")
    if data["Watch_Date"].isna().any():
        raise ValueError("Some Watch_Date values are missing or are not valid dates.")

    numeric_columns = ["Rating", "Watch_Time_Minutes", "Monthly_Revenue"]
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    invalid_numeric = [
        column for column in numeric_columns if data[column].isna().any()
    ]
    if invalid_numeric:
        raise ValueError(
            "Some values are missing or invalid in: " + ", ".join(invalid_numeric)
        )

    return data


if not LOGO_PATH.is_file():
    st.error(f"Could not find the logo image at `{LOGO_PATH}`.")
    st.stop()
if not BACKGROUND_PATH.is_file():
    st.error(f"Could not find the background image at `{BACKGROUND_PATH}`.")
    st.stop()

background_image = base64.b64encode(BACKGROUND_PATH.read_bytes()).decode("ascii")
st.markdown(
    """
    <style>
    .stApp {
        background-image:
            linear-gradient(rgba(8, 8, 11, 0.62), rgba(8, 8, 11, 0.76)),
            url("data:image/png;base64,__BACKGROUND_IMAGE__");
        background-size: cover;
        background-position: center top;
        background-attachment: fixed;
        color: #f5f5f7;
    }
    [data-testid="stSidebar"] {
        background: #111116;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    .block-container {
        max-width: 1440px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }
    .brand {
        color: #e50914;
        font-size: 1.15rem;
        font-weight: 900;
        letter-spacing: 0.22rem;
        margin-bottom: 1.6rem;
    }
    [data-testid="stSidebar"] img {
        border-radius: 10px;
        margin: 0 auto 1.2rem;
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
    [data-testid="stDateInput"] input {
        background-color: #17171e;
        border-color: #383840;
        color: #f5f5f7;
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within > div,
    [data-testid="stMultiSelect"] div[data-baseweb="select"]:focus-within > div,
    [data-testid="stDateInput"] input:focus {
        border-color: #e50914;
        box-shadow: 0 0 0 1px #e50914;
    }
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background-color: #e50914;
        color: #ffffff;
    }
    [data-testid="stMultiSelect"] span[data-baseweb="tag"]:hover {
        background-color: #b80710;
    }
    button[kind="primary"] {
        background-color: #e50914;
        border-color: #e50914;
    }
    button[kind="primary"]:hover {
        background-color: #b80710;
        border-color: #b80710;
    }
    .eyebrow {
        color: #ff7379;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.18rem;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }
    .hero-title {
        color: #f7f7f8;
        font-size: clamp(2rem, 4vw, 3.2rem);
        font-weight: 800;
        letter-spacing: -0.06rem;
        line-height: 1.1;
        margin: 0;
    }
    .hero-title span {
        color: #e50914;
    }
    .hero-subtitle {
        color: #a6a6b0;
        font-size: 1rem;
        margin: 0.65rem 0 1.7rem;
    }
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #17171e, #121217);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1rem 1.15rem;
    }
    [data-testid="stMetricLabel"] {
        color: #a6a6b0;
    }
    [data-testid="stMetricValue"] {
        color: #f7f7f8;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(20, 20, 27, 0.78);
        border-color: rgba(255, 255, 255, 0.08);
        border-radius: 16px;
    }
    h2, h3 {
        color: #f7f7f8;
    }
    </style>
    """.replace("__BACKGROUND_IMAGE__", background_image),
    unsafe_allow_html=True,
)

if not DATA_PATH.is_file():
    st.error(f"Could not find the dataset at `{DATA_PATH}`.")
    st.stop()

try:
    netflix = load_data(DATA_PATH)
except (OSError, pd.errors.ParserError, ValueError) as error:
    st.error(f"Unable to load the Netflix dataset: {error}")
    st.stop()

if netflix.empty:
    st.error("The Netflix dataset does not contain any rows.")
    st.stop()

min_date = netflix["Watch_Date"].min().date()
max_date = netflix["Watch_Date"].max().date()

st.sidebar.image(str(LOGO_PATH), width=160)
st.sidebar.subheader("Dashboard filters")
st.sidebar.caption("Selections update every KPI and chart.")

regions = sorted(netflix["Region"].dropna().unique().tolist())
plans = sorted(netflix["Subscription_Plan"].dropna().unique().tolist())
categories = sorted(netflix["Category"].dropna().unique().tolist())

selected_regions = st.sidebar.multiselect("Region", regions, default=regions)
selected_plans = st.sidebar.multiselect(
    "Subscription plan", plans, default=plans
)
selected_categories = st.sidebar.multiselect(
    "Content category", categories, default=categories
)
selected_dates = st.sidebar.date_input(
    "Watch date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(selected_dates, (tuple, list)):
    if len(selected_dates) == 2:
        start_date, end_date = selected_dates
    elif len(selected_dates) == 1:
        start_date = end_date = selected_dates[0]
    else:
        start_date, end_date = min_date, max_date
else:
    start_date = end_date = selected_dates

filtered = netflix.loc[
    netflix["Region"].isin(selected_regions)
    & netflix["Subscription_Plan"].isin(selected_plans)
    & netflix["Category"].isin(selected_categories)
    & netflix["Watch_Date"].dt.date.between(start_date, end_date)
].copy()

st.markdown('<div class="eyebrow">Streaming data • viewing insights</div>', unsafe_allow_html=True)
st.markdown(
    '<h1 class="hero-title">Netflix <span>Insights</span></h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="hero-subtitle">A clear view of revenue, ratings, and viewing activity.</p>',
    unsafe_allow_html=True,
)

if filtered.empty:
    st.info("No records match these filters. Update the selections in the sidebar.")
    st.stop()

metric_columns = st.columns(4)
revenue_total = filtered["Monthly_Revenue"].sum()
watch_minutes = filtered["Watch_Time_Minutes"].sum()
metric_columns[0].metric("Unique customers", f"{filtered['Customer_ID'].nunique():,}")
metric_columns[1].metric("Total revenue", f"{revenue_total / 1000:.1f}K")
metric_columns[2].metric("Avg. rating", f"{filtered['Rating'].mean():.1f} / 5")
metric_columns[3].metric(
    "Watch time (min)",
    f"{watch_minutes / 1000:.1f}K",
)

st.write("")
left_chart, right_chart = st.columns(2, gap="large")

with left_chart:
    with st.container(border=True):
        st.subheader("Revenue by region")
        st.caption("Total monthly revenue grouped by customer region.")
        region_revenue = (
            filtered.groupby("Region", as_index=False)["Monthly_Revenue"]
            .sum()
            .rename(columns={"Monthly_Revenue": "Revenue"})
            .sort_values("Revenue", ascending=False)
        )
        st.bar_chart(
            region_revenue,
            x="Region",
            y="Revenue",
            color=ACCENT,
            width="stretch",
        )

with right_chart:
    with st.container(border=True):
        st.subheader("Rating points by plan")
        st.caption("Sum of customer ratings for each subscription plan.")
        plan_ratings = (
            filtered.groupby("Subscription_Plan", as_index=False)["Rating"]
            .sum()
            .rename(
                columns={
                    "Subscription_Plan": "Subscription plan",
                    "Rating": "Rating points",
                }
            )
        )
        st.vega_lite_chart(
            plan_ratings,
            {
                "mark": {
                    "type": "arc",
                    "innerRadius": 68,
                    "stroke": "#17171e",
                    "strokeWidth": 3,
                },
                "encoding": {
                    "theta": {"field": "Rating points", "type": "quantitative"},
                    "color": {
                        "field": "Subscription plan",
                        "type": "nominal",
                        "scale": {
                            "range": ["#E50914", "#FF7379", "#8F080E", "#F5A3A6"]
                        },
                        "legend": {
                            "orient": "bottom",
                            "labelColor": "#d5d5dc",
                            "title": None,
                        },
                    },
                    "tooltip": [
                        {"field": "Subscription plan", "type": "nominal"},
                        {"field": "Rating points", "type": "quantitative"},
                    ],
                },
                "view": {"stroke": None},
                "config": {"background": "transparent"},
            },
            width="stretch",
        )

left_chart, right_chart = st.columns(2, gap="large")

with left_chart:
    with st.container(border=True):
        st.subheader("Revenue by category")
        st.caption("Compare revenue across genres and content categories.")
        category_revenue = (
            filtered.groupby("Category", as_index=False)["Monthly_Revenue"]
            .sum()
            .rename(columns={"Monthly_Revenue": "Revenue"})
            .sort_values("Revenue", ascending=False)
        )
        st.bar_chart(
            category_revenue,
            x="Category",
            y="Revenue",
            color=ACCENT,
            width="stretch",
        )

with right_chart:
    with st.container(border=True):
        st.subheader("Revenue by month")
        st.caption("Monthly revenue in chronological order.")
        monthly_revenue = (
            filtered.set_index("Watch_Date")
            .resample("MS")["Monthly_Revenue"]
            .sum()
            .rename_axis("Month")
            .reset_index()
        )
        monthly_revenue["Month"] = monthly_revenue["Month"].dt.strftime("%b %Y")
        monthly_revenue = monthly_revenue.rename(
            columns={"Monthly_Revenue": "Revenue"}
        )
        st.bar_chart(
            monthly_revenue,
            x="Month",
            y="Revenue",
            color=ACCENT,
            width="stretch",
        )

with st.expander("Explore filtered records and dataset quality"):
    quality_columns = st.columns(3)
    quality_columns[0].metric("Rows in dataset", f"{len(netflix):,}")
    quality_columns[1].metric(
        "Missing values",
        f"{int(netflix.isna().sum().sum()):,}",
    )
    quality_columns[2].metric(
        "Duplicate rows",
        f"{int(netflix.duplicated().sum()):,}",
    )
    st.dataframe(filtered, width="stretch", hide_index=True)
    st.download_button(
        "Download filtered data",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="netflix_filtered.csv",
        mime="text/csv",
    )
