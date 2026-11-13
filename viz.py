"""
CodeAlpha - Data Analytics - Task 3: Data Visualization
=======================================================
A visual data story about the 1,000 books scraped in Task 1 and explored in Task 2.
All charts are made with Matplotlib + Seaborn.

Each chart function:
  * takes the DataFrame and returns a Matplotlib Figure
  * has an "action title" (the insight, not just the topic)
  * is used by BOTH this script (exports PNG + PDF) and the Streamlit app

Run from cmd:
    python viz.py
Creates:
    charts/01_*.png ... charts/09_dashboard.png   (high-resolution, 200 dpi)
    charts/BookScope_Visual_Portfolio.pdf          (all charts in one PDF)
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw charts without opening windows

import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch

BASE = Path(__file__).parent
DATA_PATH = BASE / "data" / "books.csv"
CHART_DIR = BASE / "charts"
PLACEHOLDERS = ["Default", "Add a comment"]

# --------------------------------------------------------------------------
# Design system: one place for every colour and font decision
# --------------------------------------------------------------------------
SURFACE = "#FCFCFB"     # chart background
INK = "#0B0B0B"         # titles
INK_2 = "#52514E"       # subtitles, labels
INK_3 = "#8A8984"       # footnotes
GRID = "#E9E8E4"        # hairline grid
BLUE = "#2A78D6"        # main data colour
ORANGE = "#EB6834"      # emphasis: "look here"
GREY = "#CFCDC6"        # de-emphasised data
GREEN = "#1BAF7A"       # good / opportunity
# Bundle the Inter font with the project so charts look identical on every computer
for _f in (BASE / "fonts").glob("*.otf"):
    font_manager.fontManager.addfont(str(_f))

BLUES = LinearSegmentedColormap.from_list("blues", ["#EAF2FD", "#86B6EF", "#2A78D6", "#104281"])

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.family": ["Inter", "DejaVu Sans"], "font.size": 10.5,
    "axes.edgecolor": GRID, "axes.labelcolor": INK_2, "axes.titlelocation": "left",
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8,
    "xtick.color": INK_2, "ytick.color": INK_2, "xtick.major.size": 0, "ytick.major.size": 0,
    "legend.frameon": False, "figure.dpi": 110, "axes.axisbelow": True,
})
import logging
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)  # hide "font not found" notes


def load_data(path: str | Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["is_placeholder"] = df["category"].isin(PLACEHOLDERS)
    df["price_band"] = pd.cut(df["price_gbp"], [0, 20, 30, 40, 50, 60],
                              labels=["£10–20", "£20–30", "£30–40", "£40–50", "£50–60"])
    return df


def big_genres(df, min_books=30):
    """Real genres large enough to compare (lowers the bar for small datasets)."""
    counts = df.loc[~df["is_placeholder"], "category"].value_counts()
    for t in (min_books, 10, 5, 1):
        big = list(counts[counts >= t].index)
        if len(big) >= 2:
            return big
    return list(counts.index)


def headline(fig, title: str, subtitle: str, source: bool = True):
    """Action title (the insight) + subtitle (what is shown) + source line."""
    fig.text(0.035, 0.965, title, fontsize=15.5, fontweight="bold", color=INK, va="top")
    fig.text(0.035, 0.905, subtitle, fontsize=10.5, color=INK_2, va="top")
    if source:
        fig.text(0.035, 0.025, "Source: books.toscrape.com, scraped in Task 1 (n = 1,000 books)",
                 fontsize=8.5, color=INK_3)


def new_fig(w=11, h=6.2, top=0.80, bottom=0.12, left=0.08, right=0.97):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.subplots_adjust(top=top, bottom=bottom, left=left, right=right)
    return fig, ax


# ==========================================================================
# Chapter 1: what is in the catalogue
# ==========================================================================
def chart_top_categories(df):
    counts = df["category"].value_counts().head(12).sort_values()
    colors = [ORANGE if c in PLACEHOLDERS else BLUE for c in counts.index]
    fig, ax = new_fig(h=6.4, left=0.17)
    ax.barh(counts.index, counts.values, color=colors, height=0.62)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    for y, v in enumerate(counts.values):
        ax.text(v + 1.5, y, str(v), va="center", fontsize=9.5, color=INK_2)
    for lbl in ax.get_yticklabels():
        if lbl.get_text() in PLACEHOLDERS:
            lbl.set_color(ORANGE); lbl.set_fontweight("bold")
    ax.set_xlabel("Number of books")
    ph = df["is_placeholder"].sum()
    headline(fig, "The biggest 'category' isn't a genre at all",
             f"Top 12 categories by number of books. Orange = website placeholders, holding {ph} books "
             f"({ph / len(df):.0%}) with no real genre")
    return fig


def chart_waffle_placeholder(df):
    share = df["is_placeholder"].mean()
    n_bad = round(share * 100)
    fig = plt.figure(figsize=(11, 6.2))
    ax = fig.add_axes([0.05, 0.12, 0.42, 0.68])
    ax.set_axis_off(); ax.set_aspect("equal")
    for i in range(100):
        r, c = divmod(i, 10)
        color = ORANGE if i >= 100 - n_bad else BLUE
        ax.add_patch(FancyBboxPatch((c, 9 - r), 0.82, 0.82, boxstyle="round,pad=0,rounding_size=0.14",
                                    color=color, lw=0))
    ax.set_xlim(-0.2, 10); ax.set_ylim(-0.2, 10)
    fig.text(0.53, 0.66, f"{share:.0%}", fontsize=64, fontweight="bold", color=ORANGE)
    fig.text(0.53, 0.58, "of books have no usable genre", fontsize=15, color=INK)
    fig.text(0.53, 0.47, f"{df.loc[df.category == 'Default'].shape[0]} books are filed under \"Default\"\n"
                         f"{df.loc[df.category == 'Add a comment'].shape[0]} books are filed under \"Add a comment\"",
             fontsize=11.5, color=INK_2, linespacing=1.6)
    fig.text(0.53, 0.30, "Decision: re-label these books before any\ngenre-based report or recommendation.",
             fontsize=11.5, color=INK, fontweight="bold", linespacing=1.5)
    fig.text(0.07, 0.07, "■ Real genre", color=BLUE, fontsize=10)
    fig.text(0.20, 0.07, "■ Placeholder", color=ORANGE, fontsize=10)
    headline(fig, "One in five books is invisible to genre analysis",
             "Each square = 1% of the catalogue", source=False)
    fig.text(0.53, 0.07, "Source: books.toscrape.com, scraped in Task 1 (n = 1,000 books)", fontsize=8.5, color=INK_3)
    return fig


# ==========================================================================
# Chapter 2: price
# ==========================================================================
def chart_price_distribution(df):
    fig, ax = new_fig()
    sns.histplot(df["price_gbp"], bins=np.arange(10, 62, 2), color=BLUE, edgecolor=SURFACE,
                 linewidth=1.5, ax=ax, alpha=1)
    per_bin = len(df) / 25
    ax.axhline(per_bin, color=INK_2, lw=1)
    ax.text(60.5, per_bin, f" even spread\n ≈{per_bin:.0f} per bin", va="center", fontsize=9, color=INK_2)
    med = df["price_gbp"].median()
    ax.axvline(med, color=ORANGE, lw=2)
    top = ax.get_ylim()[1] * 1.12
    ax.set_ylim(0, top)
    ax.text(med + 0.4, top * 0.97, f"median £{med:.2f}", color=ORANGE, fontsize=10, fontweight="bold", va="top",
            bbox=dict(facecolor=SURFACE, edgecolor="none", pad=2))
    ax.set_xlabel("Price (£)"); ax.set_ylabel("Number of books")
    ax.set_xlim(9, 64)
    headline(fig, "Prices are spread flat from £10 to £60: there is no 'typical' price",
             "Number of books in each £2 price bin. A real store usually peaks at low prices and has a long, thin premium tail")
    return fig


def chart_price_by_rating(df):
    fig, ax = new_fig()
    order = [1, 2, 3, 4, 5]
    sns.stripplot(data=df, x="rating", y="price_gbp", order=order, color=GREY, size=3.2, jitter=0.28, alpha=0.7, ax=ax)
    med = df.groupby("rating")["price_gbp"].median().reindex(order)
    ax.plot(range(5), med.values, color=BLUE, lw=2, marker="o", markersize=9,
            markeredgecolor=SURFACE, markeredgewidth=2, zorder=5)
    for x, v in enumerate(med.values):
        ax.text(x + 0.12, v + 1.2, f"£{v:.0f}", color=BLUE, fontsize=10, fontweight="bold")
    ax.set_xticks(range(5), [f"{r}★" for r in order])
    ax.set_xlabel("Star rating"); ax.set_ylabel("Price (£)")
    headline(fig, "A 5-star book costs the same as a 1-star book",
             "Each grey dot is one book; the blue line joins the median price at each rating (Spearman ρ = 0.03, p = 0.36)")
    return fig


def chart_price_by_category(df):
    real = df[~df["is_placeholder"]]
    big = big_genres(df)
    stats = (real[real["category"].isin(big)].groupby("category")["price_gbp"]
             .agg(median="median", q1=lambda s: s.quantile(.25), q3=lambda s: s.quantile(.75), n="size")
             .sort_values("median"))
    overall = df["price_gbp"].median()
    fig, ax = new_fig(left=0.17)
    y = np.arange(len(stats))
    ax.hlines(y, stats["q1"], stats["q3"], color="#B7D3F6", lw=7, capstyle="round")
    ax.scatter(stats["median"], y, s=90, color=BLUE, edgecolor=SURFACE, linewidth=2, zorder=3)
    ax.axvline(overall, color=ORANGE, lw=1.5)
    ax.text(overall + 0.4, len(stats) - 0.45, f"all books: £{overall:.0f}", color=ORANGE, fontsize=9.5, fontweight="bold")
    ax.set_yticks(y, [f"{c}  (n={n})" for c, n in zip(stats.index, stats["n"])])
    ax.grid(axis="y", visible=False); ax.grid(axis="x", visible=True)
    ax.set_xlabel("Price (£)"); ax.set_xlim(10, 60)
    headline(fig, "No genre is priced as 'premium': every range overlaps",
             "Median price (dot) and middle 50% of prices (bar) for the largest genres (Kruskal-Wallis p = 0.22)")
    return fig


def chart_small_sample(df):
    real = df[~df["is_placeholder"]]
    g = real.groupby("category").agg(n=("title", "size"), avg=("price_gbp", "mean")).reset_index()
    fig, ax = new_fig()
    ax.set_xscale("log")
    small = g["n"] < 5
    ax.scatter(g.loc[small, "n"], g.loc[small, "avg"], s=70, color=ORANGE, edgecolor=SURFACE, lw=1.5, label="< 5 books", zorder=3)
    ax.scatter(g.loc[~small, "n"], g.loc[~small, "avg"], s=70, color=BLUE, edgecolor=SURFACE, lw=1.5, label="5+ books", zorder=3)
    ax.axhline(df["price_gbp"].mean(), color=INK_2, lw=1)
    for _, r in g.loc[small].nlargest(2, "avg").iterrows():
        ax.annotate(f"{r['category']} ({r['n']})", (r["n"], r["avg"]), xytext=(8, 4), textcoords="offset points", fontsize=9, color=INK_2)
    for _, r in g.loc[small].nsmallest(2, "avg").iterrows():
        ax.annotate(f"{r['category']} ({r['n']})", (r["n"], r["avg"]), xytext=(8, -10), textcoords="offset points", fontsize=9, color=INK_2)
    ax.set_xticks([1, 2, 5, 10, 20, 50, 100], ["1", "2", "5", "10", "20", "50", "100"])
    ax.set_xlabel("Books in category (log scale)"); ax.set_ylabel("Average price (£)")
    ax.legend(loc="upper right")
    headline(fig, "Extreme genre averages come from genres with only 1–4 books",
             "Average price vs category size. The funnel shape shows averages settle near £35 once a genre has enough books")
    return fig


# ==========================================================================
# Chapter 3: ratings and where the opportunity is
# ==========================================================================
def chart_rating_heatmap(df):
    real = df[~df["is_placeholder"]]
    big = big_genres(df)
    ct = pd.crosstab(real.loc[real.category.isin(big), "category"], real.loc[real.category.isin(big), "rating"],
                     normalize="index").reindex(columns=[1, 2, 3, 4, 5], fill_value=0) * 100
    ct = ct.loc[ct[[4, 5]].sum(axis=1).sort_values(ascending=False).index]
    fig, ax = new_fig(left=0.17, right=0.93)
    sns.heatmap(ct, annot=True, fmt=".0f", cmap=BLUES, vmin=0, vmax=40, linewidths=2, linecolor=SURFACE,
                cbar_kws={"label": "% of genre's books", "shrink": 0.8}, annot_kws={"fontsize": 10}, ax=ax)
    ax.set_xticklabels([f"{c}★" for c in ct.columns]); ax.set_xlabel("Star rating"); ax.set_ylabel("")
    ax.tick_params(axis="y", rotation=0); ax.grid(False)
    headline(fig, "No genre is consistently better rated",
             "Share of each genre's books at each star rating, sorted by % rated 4–5★ (χ² test p = 0.58)")
    return fig


def chart_value_matrix(df):
    value = (df["rating"] >= 4) & (df["price_gbp"] <= 20)
    over = (df["rating"] <= 2) & (df["price_gbp"] >= 50)
    rng = np.random.default_rng(7)
    jitter = df["rating"] + rng.uniform(-0.28, 0.28, len(df))
    fig, ax = new_fig()
    ax.axvspan(9, 20, ymin=0.6, ymax=1, color="#E3F6EE", zorder=0)
    ax.axvspan(50, 61, ymin=0, ymax=0.4, color="#FDE9E1", zorder=0)
    ax.scatter(df.loc[~value & ~over, "price_gbp"], jitter[~value & ~over], s=14, color=GREY, lw=0)
    ax.scatter(df.loc[value, "price_gbp"], jitter[value], s=26, color=GREEN, edgecolor=SURFACE, lw=0.6)
    ax.scatter(df.loc[over, "price_gbp"], jitter[over], s=26, color=ORANGE, edgecolor=SURFACE, lw=0.6)
    box = dict(facecolor=SURFACE, edgecolor=GRID, boxstyle="round,pad=0.45")
    ax.text(21, 5.45, f"VALUE PICKS: {value.sum()} books\n4–5★ for £20 or less", color="#0E7A53", fontsize=10.5,
            fontweight="bold", va="top", bbox=box, zorder=6)
    ax.text(49, 0.55, f"OVERPRICED: {over.sum()} books\n1–2★ for £50 or more", color="#B8461C", fontsize=10.5,
            fontweight="bold", ha="right", va="bottom", bbox=box, zorder=6)
    ax.set_yticks([1, 2, 3, 4, 5], ["1★", "2★", "3★", "4★", "5★"])
    ax.set_ylim(0.4, 5.6); ax.set_xlim(9, 61)
    ax.set_xlabel("Price (£)"); ax.set_ylabel("Star rating")
    headline(fig, f"{value.sum()} high-rated books under £20 are ready for a 'Best Value' shelf",
             "Every book by price and rating. Green = promote, orange = review the price")
    return fig


# ==========================================================================
# One-page dashboard
# ==========================================================================
def chart_dashboard(df):
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 4, left=0.095, right=0.97, top=0.86, bottom=0.07, hspace=0.62, wspace=0.32,
                          height_ratios=[0.5, 1, 1])
    value = ((df["rating"] >= 4) & (df["price_gbp"] <= 20)).sum()
    tiles = [("Books scraped", f"{len(df):,}", INK), ("Median price", f"£{df.price_gbp.median():.2f}", INK),
             ("Average rating", f"{df.rating.mean():.2f}★", INK),
             ("No real genre", f"{df.is_placeholder.mean():.0%}", ORANGE)]
    for i, (lbl, val, col) in enumerate(tiles):
        ax = fig.add_subplot(gs[0, i]); ax.set_axis_off()
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.08",
                                    transform=ax.transAxes, facecolor="white", edgecolor=GRID, lw=1.2))
        ax.text(0.07, 0.68, lbl, fontsize=11, color=INK_2, transform=ax.transAxes)
        ax.text(0.07, 0.22, val, fontsize=26, fontweight="bold", color=col, transform=ax.transAxes)

    ax = fig.add_subplot(gs[1, :2])
    counts = df["category"].value_counts().head(8).sort_values()
    ax.barh(counts.index, counts.values, color=[ORANGE if c in PLACEHOLDERS else BLUE for c in counts.index], height=0.6)
    ax.grid(axis="y", visible=False); ax.grid(axis="x", visible=True)
    ax.set_title("Top categories (orange = placeholder)", fontsize=12, fontweight="bold", color=INK, pad=10)

    ax = fig.add_subplot(gs[1, 2:])
    sns.histplot(df["price_gbp"], bins=np.arange(10, 62, 2.5), color=BLUE, edgecolor=SURFACE, lw=1.2, alpha=1, ax=ax)
    ax.set_xlabel("Price (£)"); ax.set_ylabel("Books")
    ax.set_title("Price is flat from £10 to £60", fontsize=12, fontweight="bold", color=INK, pad=10)

    ax = fig.add_subplot(gs[2, :2])
    med = df.groupby("rating")["price_gbp"].median()
    ax.bar([f"{r}★" for r in med.index], med.values, color=BLUE, width=0.55)
    for x, v in enumerate(med.values):
        ax.text(x, v + 0.8, f"£{v:.0f}", ha="center", fontsize=10, color=INK_2)
    ax.set_ylim(0, 45); ax.set_ylabel("Median price (£)")
    ax.set_title("Higher rating ≠ higher price", fontsize=12, fontweight="bold", color=INK, pad=10)

    ax = fig.add_subplot(gs[2, 2:])
    r = df["rating"].value_counts().sort_index()
    ax.bar([f"{i}★" for i in r.index], r.values, color=BLUE, width=0.55)
    ax.axhline(len(df) / 5, color=INK_2, lw=1)
    ax.text(4.35, len(df) / 5 + 4, "20% line", fontsize=9, color=INK_2, ha="right")
    ax.set_ylabel("Books")
    ax.set_title(f"Ratings are evenly spread · {value} value picks (4–5★, ≤ £20)", fontsize=12, fontweight="bold", color=INK, pad=10)

    fig.text(0.095, 0.955, "BookScope: Catalogue Dashboard", fontsize=20, fontweight="bold", color=INK, va="top")
    fig.text(0.095, 0.915, "Books.toscrape.com catalogue at a glance. Data scraped in Task 1, findings from Task 2 EDA",
             fontsize=11.5, color=INK_2, va="top")
    fig.text(0.095, 0.02, "Source: books.toscrape.com (n = 1,000 books) · Built with Matplotlib + Seaborn",
             fontsize=9, color=INK_3)
    return fig


# --------------------------------------------------------------------------
# The story: order matters (context -> problem -> insight -> decision)
# --------------------------------------------------------------------------
STORY = [
    {"key": "01_top_categories", "chapter": "1 · The catalogue", "fn": chart_top_categories,
     "so_what": "Category data has a quality problem: the largest group is a placeholder. Any 'best genre' report would be wrong.",
     "decision": "Clean category labels first (fix 'Default' and 'Add a comment')."},
    {"key": "02_missing_genre", "chapter": "1 · The catalogue", "fn": chart_waffle_placeholder,
     "so_what": "About 1 in 5 books cannot be found by browsing genres, which hurts discoverability.",
     "decision": "Scrape each book's detail page or tag them manually to assign a real genre."},
    {"key": "03_price_distribution", "chapter": "2 · Pricing", "fn": chart_price_distribution,
     "so_what": "There's no budget tier or premium tier. Prices look randomly set rather than planned.",
     "decision": "Define clear price tiers (e.g. under £20 / £20–40 / £40+) to guide customers."},
    {"key": "04_price_by_rating", "chapter": "2 · Pricing", "fn": chart_price_by_rating,
     "so_what": "Customers paying more do not get better-rated books. Price is not a quality signal here.",
     "decision": "Use rating, not price, to highlight quality (badges, 'Top rated' filter)."},
    {"key": "05_price_by_category", "chapter": "2 · Pricing", "fn": chart_price_by_category,
     "so_what": "Every major genre covers the full £10–£60 range, so genre does not explain price either.",
     "decision": "If genre-based pricing is wanted, it has to be designed. It doesn't exist today."},
    {"key": "06_small_sample_trap", "chapter": "2 · Pricing", "fn": chart_small_sample,
     "so_what": "Genres like 'Novels' or 'Erotica' look cheap or expensive only because they contain 1 book.",
     "decision": "Merge tiny genres into broader ones before comparing averages."},
    {"key": "07_rating_heatmap", "chapter": "3 · Ratings & opportunity", "fn": chart_rating_heatmap,
     "so_what": "Ratings are spread similarly in every genre, with no 'quality genre' to push.",
     "decision": "Promote individual books, not whole genres."},
    {"key": "08_value_matrix", "chapter": "3 · Ratings & opportunity", "fn": chart_value_matrix,
     "so_what": "Because price and rating are unrelated, there are clear bargains and clear over-priced books.",
     "decision": "Launch a 'Best Value' shelf and review prices of the over-priced low-rated books."},
    {"key": "09_dashboard", "chapter": "Summary", "fn": chart_dashboard,
     "so_what": "One page with the four numbers and four charts a manager needs.",
     "decision": "Use as the executive summary slide."},
]


def export_all(df: pd.DataFrame, folder: Path = CHART_DIR) -> list[Path]:
    folder.mkdir(parents=True, exist_ok=True)
    paths = []
    pdf_path = folder / "BookScope_Visual_Portfolio.pdf"
    with PdfPages(pdf_path) as pdf:
        for item in STORY:
            fig = item["fn"](df)
            path = folder / f"{item['key']}.png"
            fig.savefig(path, dpi=200)
            pdf.savefig(fig)
            plt.close(fig)
            paths.append(path)
            print(f"  ✓ {path.name}")
    paths.append(pdf_path)
    print(f"  ✓ {pdf_path.name}")
    return paths


if __name__ == "__main__":
    print("Building the visual portfolio ...")
    export_all(load_data())
    print(f"Done. Charts saved in: {CHART_DIR}")
