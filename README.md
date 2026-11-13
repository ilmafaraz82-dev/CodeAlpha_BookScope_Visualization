# 🎨 BookScope: A Data Story
### CodeAlpha · Data Analytics Internship · Task 3: Data Visualization

A **visualization portfolio and data story** built from the **1,000 books** scraped in Task 1
and explored in Task 2. Nine charts made with **Matplotlib + Seaborn** answer one business question:

> **What should this bookstore do with its catalogue?**

The charts are presented in an interactive **Streamlit** app and exported as **high-resolution PNGs**
and a **PDF portfolio**.

---

## 🎯 Task requirements → where they are covered

| CodeAlpha requirement | How it is done here |
|---|---|
| Transform raw data into charts, graphs and dashboards | 8 story charts + 1 one-page dashboard, from the raw `books.csv` |
| Use tools like Matplotlib, Seaborn | Every chart is drawn with Matplotlib + Seaborn (`viz.py`) |
| Design visuals that enhance understanding | Action titles, one emphasis colour, less ink, selective labels (see 🎨 Design choices tab) |
| Craft compelling data stories that support decision-making | 3 chapters (context → problem → insight → decision); every chart has a *So what?* and a *Decision* |
| Build a strong portfolio | `charts/` folder: 9 PNGs at 200 dpi + `BookScope_Visual_Portfolio.pdf` |

---

## 📖 The story

| # | Chart | Action title (the insight) | Decision |
|---|---|---|---|
| 1 | Horizontal bar | The biggest 'category' isn't a genre at all | Clean category labels |
| 2 | Waffle chart | One in five books is invisible to genre analysis (22%) | Assign real genres |
| 3 | Histogram | Prices are spread flat from £10 to £60 | Create price tiers |
| 4 | Strip plot + median line | A 5-star book costs the same as a 1-star book | Use rating, not price, to signal quality |
| 5 | Dot + range plot | No genre is priced as 'premium' | Genre pricing must be designed |
| 6 | Log-scale scatter | Extreme genre averages come from genres with 1–4 books | Merge tiny genres |
| 7 | Heatmap | No genre is consistently better rated | Promote books, not genres |
| 8 | Scatter with zones | **75** high-rated books under £20 → 'Best Value' shelf | Launch shelf, review **74** overpriced books |
| 9 | Dashboard | One-page summary | Executive summary slide |

---

## 📁 Project structure

```
CodeAlpha_ProjectName - data analytics (task 3)/
├── viz.py                 # all 9 charts (Matplotlib + Seaborn) + export to PNG/PDF
├── app.py                 # Streamlit data-story app
├── data/books.csv         # dataset from Task 1
├── fonts/                 # Inter font (OFL licence) so charts look the same on every PC
├── charts/                # created by: python viz.py
│   ├── 01_top_categories.png … 09_dashboard.png
│   └── BookScope_Visual_Portfolio.pdf
├── requirements.txt
├── .streamlit/config.toml
└── README.md
```

## ⚙️ Setup & run (Windows cmd)

```cmd
cd "C:\Users\ILMA FARAZ\OneDrive\Desktop\CodeAlpha_ProjectName - data analytics (task 3)"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

python viz.py           :: builds all charts into the charts\ folder (PNG + PDF)
streamlit run app.py    :: opens the data-story app at http://localhost:8501
```
> PowerShell: activate with `.\venv\Scripts\Activate.ps1`
>
> Tip: the sidebar button **Rebuild all charts** does the same as `python viz.py`.

## 🖥️ App tabs

- **📖 Data story:** 8 charts in story order, each with *So what?* and *Decision*
- **📊 Dashboard:** one-page dashboard with filters (category, rating, price) right above it
- **🛠️ Chart builder:** pick a chart type and options; the Matplotlib/Seaborn chart **and its Python code** are generated live
- **🎯 Decisions:** 6 prioritised recommendations + the top 15 'Best Value' books
- **🖼️ Portfolio:** gallery of all 9 charts, each downloadable, plus a PDF of all of them
- **🎨 Design choices:** colour system, design rules and why each chart type was chosen

## 🎨 Design principles used

1. **Action titles:** the title says the insight, not the topic.
2. **One emphasis colour:** orange only for what matters; blue for data; grey for context.
3. **Less ink:** no top/right spines, light grid, no 3D, shadows or rainbow colours.
4. **Selective labels:** label medians and totals, not every point.
5. **Honest axes:** bars start at 0, no dual axes, log scale clearly labelled.
6. **Accessible:** meaning never relies on colour alone (text and position too).
7. **Reproducible:** `python viz.py` rebuilds everything from the CSV.

## 🛠️ Tech stack
`Python` · `Matplotlib` · `Seaborn` · `pandas` · `NumPy` · `Streamlit`

## 👤 Author
**Ilma Faraz**, CodeAlpha Data Analytics Intern
