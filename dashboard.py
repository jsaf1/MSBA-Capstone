import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import plotly.express as px

from plotly.colors import sequential
blues_palette = sequential.Blues[::-1][:5]  # Darker blues
custom_palette = [
    "#003f5c",  # dark blue
    "#2f4b7c",  # steel blue
    "#669bbc",  # soft blue
    "#d72638",  # vivid red
    "#f46060",  # softer red
    "#adb5bd",  # medium grey
    "#dee2e6",  # light grey
    "#6c757d",  # dark grey
]


# --- Page Config ---
st.set_page_config(page_title="SKF Violations Dashboard", layout="wide")

# --- Load Data ---
data = pd.read_csv('Cleaned_SKF_data.csv')
data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
data["Year"] = data["Date"].dt.year
data["Month"] = data["Date"].dt.month_name()
data["Month_Num"] = data["Date"].dt.month  # for sorting months chronologically

# --- Sidebar Filters ---
st.sidebar.title("🔎 Filters")
section = st.sidebar.radio("📂 Navigate to", [
    "Overview", "Trends", "Violation Patterns", "Cross Analysis", "Governance", "Topics & Themes", "Raw Data"])

# Country Filter
all_countries = sorted(data["Country"].dropna().unique())
selected_country = st.sidebar.multiselect("Select Country", options=all_countries)
if st.sidebar.button("Select All Countries"):
    selected_country = all_countries

# Year Filter
all_years = sorted(data["Year"].dropna().unique())
selected_year = st.sidebar.multiselect("Select Year", options=all_years)
if st.sidebar.button("Select All Years"):
    selected_year = all_years

# Filter data by selected years first to constrain month options
month_filter_data = data.copy()
if selected_year:
    month_filter_data = month_filter_data[month_filter_data["Year"].isin(selected_year)]

month_order = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
available_months = month_filter_data["Month"].dropna().unique()
selected_month = st.sidebar.multiselect("Select Month", options=[m for m in month_order if m in available_months])
if st.sidebar.button("Select All Months"):
    selected_month = [m for m in month_order if m in available_months]

# --- Filter Dataset ---
filtered_data = data.copy()
if selected_country:
    filtered_data = filtered_data[filtered_data["Country"].isin(selected_country)]
if selected_year:
    filtered_data = filtered_data[filtered_data["Year"].isin(selected_year)]
if selected_month:
    filtered_data = filtered_data[filtered_data["Month"].isin(selected_month)]


# --- Section Logic ---
if section == "Overview":
    st.title("📊 SKF Violations Dashboard")
    st.markdown("### Key Metrics")
    
    st.markdown(
        """
        <div style="font-size: 0.85em; color: #AAAAAA; margin-top: -10px; margin-bottom: 10px;">
            <em>Note:</em> <code>Reported Violations</code> refers to unique <code>Violation_ID</code>s. All other metrics and charts reflect individual victims.
        </div>
        """,
        unsafe_allow_html=True
    )


    col1, col2, col3 = st.columns(3)
    col1.metric("🔔 Reported Violations", f"{filtered_data['Violation_ID'].nunique():,}")
    col2.metric("👥 Total Victims", f"{int(filtered_data['Total_Victims'].sum()):,}")
    col3.metric("🌍 Countries Covered", filtered_data['Country'].nunique())

    st.markdown("---")
    st.markdown("### Distribution Highlights")

    # Gender pie chart
    gender_counts = filtered_data["Gender"].value_counts().reset_index()
    gender_counts.columns = ["Gender", "Count"]
    fig_gender = px.pie(
        gender_counts,
        names="Gender",
        values="Count",
        title="Gender Distribution of Victims",
        hole=0.4,
        color_discrete_sequence=custom_palette
    )
    
    fig_gender.update_traces(
    textinfo="percent+label",
    hole=0.4,
    marker=dict(colors=["#064e66", "#39567b", "#6f97b3"]),
    domain=dict(x=[0, 0.75])  # keep pie left, occupy 75% of width
    )
    
    fig_gender.update_layout(
    legend=dict(
        x=0.65,  # Move horizontally (0 = left, 1 = right)
        y=0.75,  # Move vertically (0 = bottom, 1 = top)
        xanchor="left",  # Anchor the legend's x-position
        yanchor="middle"  # Anchor the legend's y-position
        )
    )

    # Top 5 Violation Types
    top_violations = filtered_data["Violation_Nature"].value_counts().nlargest(5).reset_index()
    top_violations.columns = ["Violation Type", "Count"]
    fig_violations = px.bar(
        top_violations,
        x="Count",
        y="Violation Type",
        orientation="h",
        title="Top 5 Violation Types",
        color_discrete_sequence=["#1f77b4"]  # Replace with your preferred color
    )
    fig_violations.update_layout(yaxis=dict(autorange="reversed"), xaxis_title=None, yaxis_title=None)

    # Top 5 Countries as pie
    top_countries = filtered_data["Country"].value_counts().nlargest(5).reset_index()
    top_countries.columns = ["Country", "Count"]
    fig_countries = px.pie(
        top_countries,
        names="Country",
        values="Count",
        title="Top 5 Affected Countries",
        hole=0.4,
        color_discrete_sequence=custom_palette  # Use your defined palette
    )

    fig_countries.update_traces(
        textinfo="percent+label",
        hole=0.4,
        marker=dict(colors=["#064e66", "#39567b", "#6f97b3", "#c0392b", "#7f8c8d"]),
        domain=dict(x=[0, 0.75])
    )

    fig_countries.update_layout(
        legend=dict(
            x=0.65,
            y=0.75,
            xanchor="left",
            yanchor="middle"
        )
    )


    # Top 5 Attackers
    top_attackers = filtered_data["Attackers"].value_counts().nlargest(5).reset_index()
    top_attackers.columns = ["Attacker", "Count"]
    fig_attackers = px.bar(
        top_attackers,
        x="Count",
        y="Attacker",
        orientation="h",
        title="Top 5 Attacker Groups",
        color_discrete_sequence=["#1f77b4"]  # or use a consistent shade like in other bar
    )
    fig_attackers.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title=None,
        yaxis_title=None
    )


    # Display charts
    col4, col5 = st.columns(2)
    col4.plotly_chart(fig_gender, use_container_width=True)
    col5.plotly_chart(fig_violations, use_container_width=True)

    col6, col7 = st.columns(2)
    col6.plotly_chart(fig_countries, use_container_width=True)
    col7.plotly_chart(fig_attackers, use_container_width=True)




elif section == "Trends":
    st.title("📈 Trends Over Time")
    chart_choice = st.radio("Select Metric", ["Violations", "Victims"], horizontal=True)
    time_granularity = st.radio("Select Time Unit", ["Yearly", "Monthly"], horizontal=True)

    if chart_choice == "Victims":
        group_col = "Total_Victims"
        chart_title_y = "Total Victims"
    else:
        group_col = "Violation_ID"
        chart_title_y = "Total Violations"

    if time_granularity == "Yearly":
        grouped = (
            filtered_data.groupby(["Year", "Country"])[group_col]
            .agg("sum" if group_col == "Total_Victims" else "nunique")
            .reset_index(name=chart_title_y)
        )
        x_col = "Year"
    else:
        grouped = (
            filtered_data.groupby(["Year", "Month", "Month_Num", "Country"])[group_col]
            .agg("sum" if group_col == "Total_Victims" else "nunique")
            .reset_index(name=chart_title_y)
        )
        # Sort months chronologically
        grouped = grouped.sort_values(by=["Year", "Month_Num"])
        grouped["Month_Year"] = pd.to_datetime(grouped["Year"].astype(str) + "-" + grouped["Month_Num"].astype(str) + "-01")
        x_col = "Month_Year"

    fig = px.line(
        grouped,
        x=x_col,
        y=chart_title_y,
        color="Country",
        markers=True,
        title=f"{time_granularity} {chart_title_y} by Country",
        color_discrete_sequence=custom_palette
    )
    fig.update_layout(legend_title_text=None, xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig, use_container_width=True)





elif section == "Violation Patterns":
    st.title("📌 Violation Patterns")
    st.markdown("### Top 5 Violation Types Over Time")

    # Top 5 Violation Types overall (for clarity)
    top_violation_types = filtered_data["Violation_Nature"].value_counts().nlargest(5).index

    # Filter data to only top violations
    violations_over_time = filtered_data[filtered_data["Violation_Nature"].isin(top_violation_types)]

    # Group by Year and Violation Type
    grouped_violations = (
        violations_over_time
        .groupby(["Year", "Violation_Nature"])["Violation_ID"]
        .nunique()
        .reset_index(name="Count")
    )

    # Bar chart: stacked by violation type per year
    fig_vio_time = px.bar(
        grouped_violations,
        x="Year",
        y="Count",
        color="Violation_Nature",
        title="",
        color_discrete_sequence=["#1f77b4", "#c0392b", "#6f97b3", "#7f8c8d", "#39567b"]
    )

    fig_vio_time.update_layout(
        xaxis_title=None,
        yaxis_title=None
    )

    st.plotly_chart(fig_vio_time, use_container_width=True)



    st.markdown("### Top Violation Types by Attacker Group")

    # Top attackers and violations
    top_attackers = filtered_data["Attackers"].value_counts().nlargest(6).index
    top_violations = filtered_data["Violation_Nature"].value_counts().nlargest(6).index

    # Filter the dataset
    filtered_cross = filtered_data[
        filtered_data["Attackers"].isin(top_attackers) &
        filtered_data["Violation_Nature"].isin(top_violations)
    ]

    # Group and prepare the data
    grouped = (
        filtered_cross.groupby(["Violation_Nature", "Attackers"])
        .size()
        .reset_index(name="Count")
    )

    # Sort violation types by total count
    violation_order = (
        grouped.groupby("Violation_Nature")["Count"].sum()
        .sort_values(ascending=False)
        .index.tolist()
    )

    # Sort attacker groups by total count
    attacker_order = (
        grouped.groupby("Attackers")["Count"].sum()
        .sort_values(ascending=False)
        .index.tolist()
    )

    # Create stacked bar chart
    fig_stacked = px.bar(
        grouped,
        x="Count",
        y="Violation_Nature",
        color="Attackers",
        title="",
        orientation="h",
        category_orders={
            "Violation_Nature": violation_order,
            "Attackers": attacker_order
        },
        color_discrete_sequence=custom_palette
    )

    fig_stacked.update_layout(xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig_stacked, use_container_width=True)


    st.markdown("### Top Violation Types by Victim Occupation")

    # Get top violation types and occupations
    top_violations = filtered_data["Violation_Nature"].value_counts().nlargest(10).index
    top_occupations = filtered_data["Victim_Occupation"].value_counts().nlargest(10).index

    # Filter data
    filtered_vo = filtered_data[
        filtered_data["Violation_Nature"].isin(top_violations) &
        filtered_data["Victim_Occupation"].isin(top_occupations)
    ]

    # Group and aggregate
    grouped_vo = (
        filtered_vo.groupby(["Violation_Nature", "Victim_Occupation"])
        .size()
        .reset_index(name="Count")
    )

    # Sort violations for consistent order
    violation_order = (
        grouped_vo.groupby("Violation_Nature")["Count"]
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )

    # Plot horizontal stacked bar chart
    fig_vo = px.bar(
        grouped_vo,
        x="Count",
        y="Violation_Nature",
        color="Victim_Occupation",
        orientation="h",
        title="",
        category_orders={"Violation_Nature": violation_order},
        color_discrete_sequence=custom_palette
    )
    fig_vo.update_layout(xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig_vo, use_container_width=True)



elif section == "Cross Analysis":
    st.title("🔍 Cross Analysis")
    st.markdown("### Top Violation Types by Country")

    # Top 10 countries and violations
    top_countries = filtered_data["Country"].value_counts().nlargest(10).index
    top_violations = filtered_data["Violation_Nature"].value_counts().nlargest(10).index

    # Filter
    filtered_vc = filtered_data[
        filtered_data["Country"].isin(top_countries) &
        filtered_data["Violation_Nature"].isin(top_violations)
    ]

    # Pivot
    heatmap_vc = (
        filtered_vc.pivot_table(
            index="Violation_Nature",
            columns="Country",
            values="Violation_ID",
            aggfunc="nunique",
            fill_value=0
        )
        .reindex(index=top_violations)
    )

    # Plot
    fig_vc = px.imshow(
        heatmap_vc,
        labels=dict(x="Country", y="Violation Type", color="Number of Violations"),
        color_continuous_scale=blues_palette[::-1],
        title=""
    )
    fig_vc.update_layout(xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig_vc, use_container_width=True)


    st.markdown("### Attacker Groups by Victim Occupation")

    # Top 10 attacker groups and occupations
    top_attackers = filtered_data["Attackers"].value_counts().nlargest(10).index
    top_occupations = filtered_data["Victim_Occupation"].value_counts().nlargest(10).index

    # Filter
    filtered_ao = filtered_data[
        filtered_data["Attackers"].isin(top_attackers) &
        filtered_data["Victim_Occupation"].isin(top_occupations)
    ]

    # Pivot
    heatmap_ao = (
        filtered_ao.pivot_table(
            index="Attackers",
            columns="Victim_Occupation",
            values="Violation_ID",
            aggfunc="nunique",
            fill_value=0
        )
        .reindex(index=top_attackers)
    )

    # Plot
    fig_ao = px.imshow(
        heatmap_ao,
        labels=dict(x="Victim Occupation", y="Attacker", color="Number of Violations"),
        color_continuous_scale=blues_palette[::-1],
        title=""
    )
    fig_ao.update_layout(xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig_ao, use_container_width=True)

    # Add spacing between sections
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### Gender Distribution by Violation Type vs Attacker Group")


    # === Left Plot: Violation Type by Gender ===
    top_violations_gender = filtered_data["Violation_Nature"].value_counts().nlargest(10).index
    filtered_gender = filtered_data[filtered_data["Violation_Nature"].isin(top_violations_gender)]

    heatmap_data_viol = (
        filtered_gender.pivot_table(
            index="Violation_Nature",
            columns="Gender",
            values="Violation_ID",
            aggfunc="nunique",
            fill_value=0
        )
        .reindex(index=top_violations_gender)
    )

    fig_viol_gender = px.imshow(
        heatmap_data_viol,
        labels=dict(x="Gender", y="Violation Type", color="Number of Violations"),
        x=heatmap_data_viol.columns,
        y=heatmap_data_viol.index,
        color_continuous_scale=blues_palette[::-1]
    )
    fig_viol_gender.update_layout(title="Violation Types by Gender", xaxis_title=None, yaxis_title=None)

    # === Right Plot: Attacker by Gender ===
    top_attackers_gender = filtered_data["Attackers"].value_counts().nlargest(10).index
    filtered_ag = filtered_data[filtered_data["Attackers"].isin(top_attackers_gender)]

    heatmap_data_attacker = (
        filtered_ag.pivot_table(
            index="Attackers",
            columns="Gender",
            values="Violation_ID",
            aggfunc="nunique",
            fill_value=0
        )
        .reindex(index=top_attackers_gender)
    )

    fig_attacker_gender = px.imshow(
        heatmap_data_attacker,
        labels=dict(x="Gender", y="Attacker", color="Number of Violations"),
        x=heatmap_data_attacker.columns,
        y=heatmap_data_attacker.index,
        color_continuous_scale=blues_palette[::-1]
    )
    fig_attacker_gender.update_layout(title="Attackers by Gender", xaxis_title=None, yaxis_title=None)

    # === Side-by-side layout ===
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig_viol_gender, use_container_width=True)
    col2.plotly_chart(fig_attacker_gender, use_container_width=True)




elif section == "Governance":
    st.title("🏛️ Governance & Indices")    

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # Indicator name mapping
    indicator_names = {
        "WB_VA": "Voice and Accountability",
        "WB_PS": "Political Stability & Absence of Violence",
        "WB_GovE": "Government Effectiveness",
        "WB_RQ": "Regulatory Quality",
        "WB_RoL": "Rule of Law",
        "WB_CoC": "Control of Corruption"
    }

    wb_cols = list(indicator_names.keys())
    country_avgs = (
        filtered_data.groupby("Country")[wb_cols]
        .mean()
        .round(2)
        .reset_index()
    )

    # Add spacing after section title and before subtitle
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### World Bank Scores by Country")
    st.markdown("<br>", unsafe_allow_html=True)

    # Create 2x3 subplot grid
    fig_grid = make_subplots(
        rows=2, cols=3,
        subplot_titles=[indicator_names[col] for col in wb_cols],
        horizontal_spacing=0.08, vertical_spacing=0.15
    )

    # Populate each subplot
    for i, col in enumerate(wb_cols):
        r = i // 3 + 1
        c = i % 3 + 1
        fig_grid.add_trace(
            go.Bar(
                x=country_avgs["Country"],
                y=country_avgs[col],
                marker_color='steelblue'
            ),
            row=r, col=c
        )
        fig_grid.update_yaxes(
            showgrid=False,
            title_text=None,
            showticklabels=True,
            row=r, col=c
        )
        fig_grid.update_xaxes(showgrid=False, row=r, col=c)

    # Final layout tweaks
    fig_grid.update_layout(
        showlegend=False,
        height=600,
        margin=dict(t=50, b=40),
    )

    st.plotly_chart(fig_grid, use_container_width=True)


    # Add spacing after the grid
    st.markdown("<br>", unsafe_allow_html=True)

    # Add spacing after the grid
    st.markdown("<br>", unsafe_allow_html=True)

    import plotly.express as px

    # Rename columns for display
    renamed_cols = {
        "RSF_Score": "RSF Freedom Score",
        "WB_VA": "Voice and Accountability",
        "WB_PS": "Political Stability & No Violence",
        "WB_GovE": "Government Effectiveness",
        "WB_RQ": "Regulatory Quality",
        "WB_RoL": "Rule of Law",
        "WB_CoC": "Control of Corruption"
    }

    # Select relevant columns and drop missing
    corr_data = filtered_data[list(renamed_cols.keys())].dropna()
    corr_matrix = corr_data.corr().rename(columns=renamed_cols, index=renamed_cols)

    # Plot interactive heatmap
    fig_corr = px.imshow(
        corr_matrix,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale=blues_palette[::-1],
        labels=dict(x="Indicator", y="Indicator", color="Correlation"),
        title="Correlation Matrix – RSF and Governance Scores"
    )

    # Improve layout
    fig_corr.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        xaxis_tickangle=45,
        margin=dict(t=80, l=20, r=20, b=20)
    )

    st.plotly_chart(fig_corr, use_container_width=True)



elif section == "Topics & Themes":
    st.title("🧠 NLP: Topics & Themes")
    st.markdown("### Interactive Topic Lexicon")

    # Load top words from CSV
    topic_words_df = pd.read_csv("Topic_TopWords.csv")

    # Manually remove common Arabic stopwords missed during preprocessing
    custom_stopwords = {"ها", "نا", "ال", "وا", "عن", "في", "من", "الى", "على", "و", "هو", "هي", "ذلك"}
    topic_words_df = topic_words_df[~topic_words_df["Word"].isin(custom_stopwords)]

    # Map topic number to label
    custom_labels = {
        0: "Airstrikes / Military",
        1: "Lebanese Legal Affairs",
        2: "Security / Surveillance",
        3: "Judicial Proceedings",
        4: "Home Raids / Arrests",
        5: "Military / Clashes",
        6: "Torture / Abuse",
        7: "Jordan / Political / Media",
        8: "Threats / Harassment",
        9: "Detainment Sites / Testimonies"
    }

    # Assign readable labels and drop unmapped rows
    topic_words_df["Label"] = topic_words_df["Topic"].map(custom_labels)
    topic_words_df = topic_words_df.dropna(subset=["Label"])

    # Color palette for labels (including fallback gray)
    color_map = {
        "Airstrikes / Military": "#1f77b4",
        "Lebanese Legal Affairs": "#ff7f0e",
        "Security / Surveillance": "#2ca02c",
        "Judicial Proceedings": "#d62728",
        "Home Raids / Arrests": "#9467bd",
        "Military / Clashes": "#8c564b",
        "Torture / Abuse": "#e377c2",
        "Jordan / Political / Media": "#7f7f7f",
        "Threats / Harassment": "#bcbd22",
        "Detainment Sites / Testimonies": "#17becf"
    }

    # Assign colors based on label
    topic_words_df["Color"] = topic_words_df["Label"].map(color_map)

    # Normalize font sizes based on Weight
    max_font = 45
    min_font = 18
    topic_words_df["FontSize"] = (
        ((topic_words_df["Weight"] - topic_words_df["Weight"].min()) /
         (topic_words_df["Weight"].max() - topic_words_df["Weight"].min())) *
        (max_font - min_font) + min_font
    )

    # Random layout
    np.random.seed(42)
    topic_words_df["x"] = np.random.rand(len(topic_words_df))
    topic_words_df["y"] = np.random.rand(len(topic_words_df))

    # Filter by topic
    all_labels = topic_words_df["Label"].unique().tolist()
    selected_label = st.selectbox("Select a Topic", ["All"] + all_labels)

    if selected_label != "All":
        filtered_df = topic_words_df[topic_words_df["Label"] == selected_label]
    else:
        filtered_df = topic_words_df

    # Plot words
    fig_words = go.Figure()
    for _, row in filtered_df.iterrows():
        fig_words.add_trace(
            go.Scatter(
                x=[row["x"]],
                y=[row["y"]],
                mode="text",
                text=[row["Word"]],
                textfont=dict(size=row["FontSize"], color=row["Color"]),
                hovertemplate=f"<b>{row['Word']}</b><br>Topic: {row['Label']}<br>Weight: {round(row['Weight'], 3)}",
                showlegend=False
            )
        )

    fig_words.update_layout(
        height=600,
        plot_bgcolor="rgb(40, 40, 40)",
        paper_bgcolor="rgb(40, 40, 40)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=10, r=10, t=20, b=20),
    )

    st.plotly_chart(fig_words, use_container_width=True)




elif section == "Raw Data":
    st.title("📄 Raw Data Table")
    st.dataframe(filtered_data)
    csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "filtered_data.csv", "text/csv")
