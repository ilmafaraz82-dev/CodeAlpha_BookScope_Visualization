"""
CodeAlpha - Data Analytics - Task 3: Data Visualization
Interactive data-story app. All charts come from viz.py (Matplotlib + Seaborn).

Run from cmd:
    streamlit run app.py
"""

import io

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from matplotlib.backends.backend_pdf import PdfPages

import viz

st.set_page_config(page_title="BookScope · Data Story", page_icon="🎨", layout="wide")

# --------------------------------------------------------------------------
# Styling (same design system as Tasks 1 and 2)
# --------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stMarkdown { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 2rem; max-width: 1200px; }
.hero { background: linear-gradient(135deg, #312E81 0%, #4F46E5 55%, #0EA5E9 100%);
  border-radius: 20px; padding: 32px 38px; color: white; margin-bottom: 24px;
  box-shadow: 0 12px 30px rgba(79,70,229,.25); }
.hero .tag { display:inline-block; background: rgba(255,255,255,.18); padding: 4px 12px;
  border-radius: 999px; font-size: 12px; font-weight: 600; letter-spacing: .5px; }
.hero h1 { color: white; font-size: 36px; font-weight: 800; margin: 12px 0 6px 0; }
.hero p { color: rgba(255,255,255,.9); font-size: 16px; margin: 0; max-width: 780px; }

.kpi { background: white; border: 1px solid #E5E7EB; border-radius: 16px; padding: 16px 20px; }
.kpi .label { color:#6B7280; font-size: 13px; font-weight: 500; }
.kpi .value { color:#111827; font-size: 26px; font-weight: 800; margin-top: 4px; }
.kpi .sub { color:#6B7280; font-size: 12px; margin-top: 2px; }

.chapter { display:inline-block; background:#EEF2FF; color:#4F46E5; font-weight:700; font-size:12px;
  letter-spacing:.4px; border-radius:999px; padding:4px 12px; margin: 18px 0 8px 0; text-transform: uppercase; }
.sowhat, .decision { border-radius:14px; padding:14px 18px; font-size:14.5px; height:100%; }
.sowhat { background:#F9FAFB; border:1px solid #E5E7EB; color:#374151; }
.decision { background:#F0FDF4; border:1px solid #BBF7D0; color:#065F46; }
.sowhat b, .decision b { display:block; font-size:12px; letter-spacing:.5px; text-transform:uppercase; margin-bottom:4px; }
.divider { border-top:1px solid #E5E7EB; margin: 30px 0 4px 0; }

.card { background:white; border:1px solid #E5E7EB; border-radius:16px; padding:18px 20px; margin-bottom:14px; }
.card h4 { margin:0 0 6px 0; color:#111827; font-size:16px; }
.card p { margin:4px 0; color:#4B5563; font-size:14px; }
.swatch { display:inline-block; width:100%; height:54px; border-radius:12px; margin-bottom:6px; }

.stTabs [data-baseweb="tab-list"] { gap: 6px; flex-wrap: wrap; }
.stTabs [data-baseweb="tab"] { background:#F3F4F6; border-radius:10px; padding:10px 18px; font-weight:600; }
.stTabs [aria-selected="true"] { background:#4F46E5 !important; color:white !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display:none; }
section[data-testid="stSidebar"] { background:#F8FAFC; }
</style>
""",
    unsafe_allow_html=True,
)


def kpi(col, label, value, sub=""):
    col.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div>'
                 f'<div class="sub">{sub}</div></div>', unsafe_allow_html=True)


@st.cache_data
def get_data(source):
    return viz.load_data(source)


@st.cache_data(show_spinner="Drawing chart ...")
def render(key: str, df: pd.DataFrame, dpi: int = 160):
    """Draw one chart from the story and return (PNG bytes, error message)."""
    fn = next(item["fn"] for item in viz.STORY if item["key"] == key)
    try:
        fig = fn(df)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi)
        plt.close(fig)
        return buf.getvalue(), None
    except Exception as err:  # show the real reason instead of failing silently
        plt.close("all")
        return None, f"{type(err).__name__}: {err}"


def chart_png(key: str, df: pd.DataFrame, use_files: bool):
    """Use the ready-made PNG in charts/ when it was built from the same data (instant), else draw it."""
    path = viz.CHART_DIR / f"{key}.png"
    if use_files and path.exists() and path.stat().st_mtime >= viz.DATA_PATH.stat().st_mtime:
        return path.read_bytes(), None
    return render(key, df)


@st.cache_data(show_spinner="Building PDF portfolio ...")
def portfolio_pdf(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with PdfPages(buf) as pdf:
        for item in viz.STORY:
            try:
                fig = item["fn"](df)
            except Exception:
                plt.close("all")
                continue
            pdf.savefig(fig)
            plt.close(fig)
    return buf.getvalue()


def show_chart(key, df, use_files):
    png, err = chart_png(key, df, use_files)
    if png is not None:
        st.image(png, width="stretch")
    else:
        st.warning("This chart could not be drawn for the current dataset.")
        with st.expander("Show error details"):
            st.code(err)
    return png


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📂 Dataset")
    upload = st.file_uploader("Use a different books.csv (optional)", type="csv")
    st.caption("Default: `data/books.csv`, scraped in Task 1.")

if upload is None and not viz.DATA_PATH.exists():
    st.error("`data/books.csv` not found. Copy it from your Task 1 folder into a `data` folder here.")
    st.stop()

df = get_data(upload if upload is not None else str(viz.DATA_PATH))
if len(df) < 50 or df["category"].nunique() < 5:
    st.warning("This dataset is very small, so some charts may look empty. Use the full 1,000-book file for best results.")

use_files = upload is None  # ready-made charts only match the default dataset
with st.sidebar:
    st.markdown("### ♻️ Charts")
    if st.button("Rebuild all charts", width="stretch",
                 help="Redraws every chart from the CSV and saves PNG + PDF into the charts folder."):
        with st.spinner("Rebuilding charts ..."):
            viz.export_all(df)
        st.cache_data.clear()
        st.success("Charts rebuilt and saved in the charts folder.")
    st.caption("Same as running `python viz.py` in cmd.")

value_picks = int(((df.rating >= 4) & (df.price_gbp <= 20)).sum())
overpriced = int(((df.rating <= 2) & (df.price_gbp >= 50)).sum())

# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
st.markdown(f"""
<div class="hero">
  <span class="tag">CODEALPHA · DATA ANALYTICS · TASK 3</span>
  <h1>🎨 BookScope: A Data Story</h1>
  <p>Turning <b>{len(df):,} scraped books</b> into clear visuals and decisions. Nine charts built with
  <b>Matplotlib + Seaborn</b> answer one question: <i>what should this bookstore do with its catalogue?</i></p>
</div>""", unsafe_allow_html=True)

k = st.columns(4)
kpi(k[0], "Charts in portfolio", f"{len(viz.STORY)}", "+ live chart builder")
kpi(k[1], "Books without a genre", f"{df.is_placeholder.mean():.0%}", "data problem to fix")
kpi(k[2], "Value picks", f"{value_picks}", "4–5★ for ≤ £20")
kpi(k[3], "Over-priced books", f"{overpriced}", "1–2★ for ≥ £50")
st.write("")

tabs = st.tabs(["📖 Data story", "📊 Dashboard", "🛠️ Chart builder", "🎯 Decisions", "🖼️ Portfolio", "🎨 Design choices"])

# ==========================================================================
# 1. The story
# ==========================================================================
with tabs[0]:
    st.markdown("##### Read top to bottom: context → problem → insight → decision")
    for i, item in enumerate(viz.STORY[:-1]):
        if i:
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(f'<span class="chapter">Chapter {item["chapter"]}</span>', unsafe_allow_html=True)
        show_chart(item["key"], df, use_files)
        a, b = st.columns(2)
        a.markdown(f'<div class="sowhat"><b>💡 So what?</b>{item["so_what"]}</div>', unsafe_allow_html=True)
        b.markdown(f'<div class="decision"><b>✅ Decision</b>{item["decision"]}</div>', unsafe_allow_html=True)

# ==========================================================================
# 2. Dashboard (filterable)
# ==========================================================================
with tabs[1]:
    st.markdown("##### Filter the dashboard. It redraws instantly.")
    f1, f2, f3 = st.columns([2, 1, 1])
    cats = f1.multiselect("Categories", sorted(df["category"].unique()), placeholder="All categories")
    rating = f2.slider("Star rating", 1, 5, (1, 5))
    price = f3.slider("Price (£)", 10, 60, (10, 60))
    view = df[df["rating"].between(*rating) & df["price_gbp"].between(price[0], price[1] + 0.99)]
    if cats:
        view = view[view["category"].isin(cats)]
    st.caption(f"Showing **{len(view):,}** of {len(df):,} books")
    if len(view) < 5:
        st.info("Too few books match these filters. Widen them to see the dashboard.")
    else:
        try:
            fig = viz.chart_dashboard(view)
            buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=150); plt.close(fig)
            st.image(buf.getvalue(), width="stretch")
            st.download_button("⬇️ Download this dashboard (PNG)", buf.getvalue(), "dashboard.png", "image/png")
        except Exception as err:
            plt.close("all")
            st.warning("These filters leave too little data for the dashboard. Widen them.")
            with st.expander("Show error details"):
                st.code(f"{type(err).__name__}: {err}")

# ==========================================================================
# 3. Chart builder (live Matplotlib + Seaborn)
# ==========================================================================
with tabs[2]:
    st.markdown("##### Build a chart live with Matplotlib + Seaborn")
    st.caption("Pick a chart and options. The chart and the exact Python code are generated on the spot.")
    b1, b2, b3 = st.columns([2, 1, 1])
    kind = b1.selectbox("Chart", ["Bar: books per category", "Bar: average price per category", "Histogram: price",
                                  "Box plot: price by rating", "Violin plot: price by rating",
                                  "Scatter: price vs rating", "Heatmap: category × rating", "Count plot: rating"])
    top_n = b2.slider("Top N categories", 3, 20, 10)
    clean = b3.toggle("Hide placeholder categories", value=True)
    data = df[~df["is_placeholder"]] if clean else df
    top = data["category"].value_counts().head(top_n).index
    fig, ax = plt.subplots(figsize=(11, 5.6))
    fig.subplots_adjust(top=0.88, bottom=0.14, left=0.17, right=0.97)
    code = ""
    try:
        if kind == "Bar: books per category":
            counts = data["category"].value_counts().head(top_n).sort_values()
            ax.barh(counts.index, counts.values, color=viz.BLUE, height=0.6)
            ax.grid(axis="y", visible=False); ax.grid(axis="x", visible=True); ax.set_xlabel("Books")
            code = f"counts = df['category'].value_counts().head({top_n}).sort_values()\nax.barh(counts.index, counts.values, color='{viz.BLUE}')"
        elif kind == "Bar: average price per category":
            avg = data[data["category"].isin(top)].groupby("category")["price_gbp"].mean().sort_values()
            ax.barh(avg.index, avg.values, color=viz.BLUE, height=0.6)
            ax.axvline(df["price_gbp"].mean(), color=viz.ORANGE, lw=1.5)
            ax.grid(axis="y", visible=False); ax.grid(axis="x", visible=True); ax.set_xlabel("Average price (£)")
            code = "avg = df.groupby('category')['price_gbp'].mean().sort_values()\nax.barh(avg.index, avg.values)\nax.axvline(df['price_gbp'].mean(), color='orange')"
        elif kind == "Histogram: price":
            bins = st.slider("Number of bins", 5, 50, 25)
            sns.histplot(data["price_gbp"], bins=bins, color=viz.BLUE, edgecolor=viz.SURFACE, alpha=1, ax=ax)
            ax.set_xlabel("Price (£)"); ax.set_ylabel("Books")
            code = f"sns.histplot(df['price_gbp'], bins={bins}, color='{viz.BLUE}', ax=ax)"
        elif kind in ("Box plot: price by rating", "Violin plot: price by rating"):
            fn = sns.boxplot if kind.startswith("Box") else sns.violinplot
            fn(data=data, x="rating", y="price_gbp", color="#B7D3F6", ax=ax)
            ax.set_xlabel("Star rating"); ax.set_ylabel("Price (£)")
            code = f"sns.{fn.__name__}(data=df, x='rating', y='price_gbp', ax=ax)"
        elif kind == "Scatter: price vs rating":
            sns.stripplot(data=data, x="price_gbp", y="rating", orient="h", order=[5, 4, 3, 2, 1],
                          color=viz.BLUE, size=3.5, jitter=0.3, alpha=0.6, native_scale=True, ax=ax)
            ax.set_xlabel("Price (£)"); ax.set_ylabel("Star rating")
            code = "sns.stripplot(data=df, x='price_gbp', y='rating', orient='h', jitter=0.3, ax=ax)"
        elif kind == "Heatmap: category × rating":
            ct = pd.crosstab(data.loc[data.category.isin(top), "category"], data.loc[data.category.isin(top), "rating"])
            sns.heatmap(ct, annot=True, fmt="d", cmap=viz.BLUES, linewidths=2, linecolor=viz.SURFACE, ax=ax)
            ax.set_xlabel("Star rating"); ax.set_ylabel(""); ax.grid(False)
            code = "ct = pd.crosstab(df['category'], df['rating'])\nsns.heatmap(ct, annot=True, fmt='d', cmap='Blues', ax=ax)"
        else:
            sns.countplot(data=data, x="rating", color="#F59E0B", ax=ax)
            ax.set_xlabel("Star rating"); ax.set_ylabel("Books")
            code = "sns.countplot(data=df, x='rating', ax=ax)"
        ax.set_title(kind, fontsize=14, fontweight="bold", color=viz.INK, loc="left", pad=12)
        buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=150)
        st.image(buf.getvalue(), width="stretch")
        st.download_button("⬇️ Download this chart (PNG)", buf.getvalue(), "chart.png", "image/png")
        st.markdown("**Code used**")
        st.code("import seaborn as sns\nimport matplotlib.pyplot as plt\nfig, ax = plt.subplots()\n" + code, language="python")
    except Exception as err:
        st.warning(f"Could not draw this chart for the current data: {err}")
    finally:
        plt.close("all")

# ==========================================================================
# 4. Decisions
# ==========================================================================
with tabs[3]:
    st.markdown("#### What the data tells the business to do")
    recs = [
        ("🏷️", "Fix category labels", "High", f"{df.is_placeholder.sum()} books sit in 'Default' / 'Add a comment'.",
         "Charts 1–2"),
        ("⭐", f"Launch a 'Best Value' shelf ({value_picks} books)", "High",
         "Price and rating are unrelated, so many great books are cheap.", "Charts 4, 8"),
        ("💷", f"Review prices of {overpriced} low-rated expensive books", "Medium",
         "1–2★ books priced at £50+ give poor value and risk bad reviews.", "Chart 8"),
        ("📐", "Create clear price tiers", "Medium", "Prices are spread flat, with no budget or premium tier.", "Charts 3, 5"),
        ("🧩", "Merge tiny genres", "Low", "Genres with 1–4 books show misleading averages.", "Chart 6"),
        ("📚", "Promote books, not genres", "Low", "No genre is rated consistently higher.", "Chart 7"),
    ]
    colors = {"High": "#FEE2E2;color:#B91C1C", "Medium": "#FEF3C7;color:#B45309", "Low": "#E0F2FE;color:#0369A1"}
    c = st.columns(2)
    for i, (icon, title, prio, why, ev) in enumerate(recs):
        c[i % 2].markdown(f"""<div class="card"><h4>{icon} {title}
<span style="float:right;font-size:12px;font-weight:700;padding:3px 10px;border-radius:999px;background:{colors[prio]}">{prio}</span></h4>
<p>{why}</p><p style="color:#9CA3AF;font-size:12.5px">Evidence: {ev}</p></div>""", unsafe_allow_html=True)

    st.markdown("#### 📋 Best Value shelf: the top 15 picks")
    picks = (df[(df.rating >= 4) & (df.price_gbp <= 20)]
             .sort_values(["rating", "price_gbp"], ascending=[False, True])
             [["title", "category", "rating", "price_gbp"]].head(15))
    st.dataframe(picks, hide_index=True, width="stretch",
                 column_config={"title": "Title", "category": "Category",
                                "rating": st.column_config.NumberColumn("Rating", format="%d ★"),
                                "price_gbp": st.column_config.NumberColumn("Price", format="£%.2f")})

# ==========================================================================
# 5. Portfolio gallery
# ==========================================================================
with tabs[4]:
    st.markdown("#### All 9 visualizations")
    pdf_file = viz.CHART_DIR / "BookScope_Visual_Portfolio.pdf"
    if use_files and pdf_file.exists() and pdf_file.stat().st_mtime >= viz.DATA_PATH.stat().st_mtime:
        pdf_bytes = pdf_file.read_bytes()
    else:
        pdf_bytes = portfolio_pdf(df)
    st.download_button("⬇️ Download full portfolio (PDF)", pdf_bytes, "BookScope_Visual_Portfolio.pdf",
                       "application/pdf", type="primary")
    st.write("")
    cols = st.columns(3)
    for i, item in enumerate(viz.STORY):
        with cols[i % 3]:
            png = show_chart(item["key"], df, use_files)
            if png is None:
                continue
            st.download_button(f"⬇️ {item['key']}.png", png, f"{item['key']}.png", "image/png",
                               key=f"dl_{item['key']}", width="stretch")
            st.write("")

# ==========================================================================
# 6. Design choices
# ==========================================================================
with tabs[5]:
    st.markdown("#### The colour system")
    sw = [(viz.BLUE, "Blue · main data"), (viz.ORANGE, "Orange · look here / problem"),
          (viz.GREEN, "Green · opportunity"), (viz.GREY, "Grey · background data"),
          ("linear-gradient(90deg,#EAF2FD,#86B6EF,#2A78D6,#104281)", "Blue scale · amounts (heatmap)")]
    c = st.columns(5)
    for col, (color, label) in zip(c, sw):
        col.markdown(f'<div class="swatch" style="background:{color}"></div><small>{label}</small>', unsafe_allow_html=True)
    st.write("")
    rules = [
        ("📰 Action titles", "Every title states the insight (\"A 5-star book costs the same as a 1-star book\"), "
                            "not just the topic (\"Price by rating\")."),
        ("🎯 One emphasis colour", "Orange is used only for what the reader must notice. Everything else is blue or grey."),
        ("🧹 Less ink", "No top/right borders, light grid lines, no 3D or shadows, so the data stands out."),
        ("🔢 Selective labels", "Only key values are labelled (medians, totals), not every point."),
        ("📏 Honest axes", "Bar charts start at 0, there are no dual y-axes, and a log scale is labelled when used."),
        ("♿ Accessible", "Colour is never the only signal: labels, text and position also carry meaning."),
        ("🧭 Story order", "Context → problem → insight → decision, the order a manager needs."),
        ("🔁 Reproducible", "One script (viz.py) rebuilds every chart from the CSV in seconds."),
    ]
    c = st.columns(2)
    for i, (t, d) in enumerate(rules):
        c[i % 2].markdown(f'<div class="card"><h4>{t}</h4><p>{d}</p></div>', unsafe_allow_html=True)
    st.markdown("#### Chart type: why each was chosen")
    st.dataframe(pd.DataFrame([
        ["Horizontal bar", "Compare categories with long names", "1, Dashboard"],
        ["Waffle chart", "Show a share (22%) that anyone can read instantly", "2"],
        ["Histogram", "Show the shape of a distribution", "3"],
        ["Strip plot + median line", "Show every book and the trend at once", "4"],
        ["Dot + range plot", "Compare medians and spread across groups", "5"],
        ["Scatter (log scale)", "Show how sample size affects averages", "6"],
        ["Heatmap", "Compare two categorical variables (genre × rating)", "7"],
        ["Scatter with highlight zones", "Turn analysis into an action list", "8"],
        ["Dashboard", "One-page summary for decision makers", "9"],
    ], columns=["Chart type", "Why", "Used in chart"]), hide_index=True, width="stretch")
