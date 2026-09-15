# Olist Product Performance Analysis

This project looks at product performance for Olist, a Brazilian e-commerce
marketplace. The goal was to figure out which products and categories are
actually selling well, how sales have moved over time, and how much of the
catalog is basically dead weight.

Tools used: SQL (SQLite), Python (pandas), Power BI.

## The question I was trying to answer

Which products/categories bring in the most orders and revenue? How has
demand changed month to month? And how many products in the catalog are
barely selling at all?

## About the data

I used the [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
from Kaggle (I used the [SQLite version](https://www.kaggle.com/datasets/terencicp/e-commerce-dataset-by-olist-as-an-sqlite-database)
so I didn't have to import 9 separate CSVs). It's licensed CC BY-NC-SA 4.0.
Covers about 99,441 orders from Sept 2016 to Oct 2018.

I didn't upload the raw dataset here since it's a bit large - see
`data/README.md` for the download link.

## How I approached it

1. Wrote the core SQL queries first (`/sql`) - KPIs, top products, revenue by
   category, monthly trend, underperformers. I only counted orders with
   status `delivered`, since anything canceled or unavailable never actually
   generated revenue.
2. Pulled those queries into Python (`/python/olist_analysis.py`) to add
   month-over-month growth %, which is a pain to do in plain SQL, and exported
   the results as CSVs.
3. Built the dashboard in Power BI using those CSVs.

## Dashboard

![Product Performance Dashboard](powerbi/dashboard_screenshot.png)

The .pbix file is in `/powerbi` if you want to open it yourself.

### A few things worth knowing about this data

- Revenue here means product price only - I left out freight/shipping since
  that's not really "product" revenue, it's a delivery cost.
- There's no actual product name field in this dataset, just category and
  size/weight - so products show up as long ID strings, not names. Kind of
  annoying but that's what we've got.
- The monthly numbers have two junk months I dropped: Sept 2016 and Dec 2016
  each only have 1 order (basically test data), and there's nothing after
  Aug 2018 because later orders hadn't been marked "delivered" yet when this
  snapshot was taken. So the trend chart only covers Jan 2017 - Aug 2018,
  which is the clean, complete stretch.
- When I say "total products," I mean products that actually sold at least
  once (32,216) - not the full catalog (32,951). About 735 products never
  sold a single unit, which felt like a separate fact worth calling out
  rather than folding into the main number.

## What I actually found

- No single category dominates - the top one (Health & Beauty) is only 9.3%
  of total revenue. Sales are pretty spread out across categories.
- Order count and revenue don't always line up. Some products get ordered a
  lot but bring in less money than pricier products that sell less often -
  Watches & Gifts is a good example of a smaller-volume, higher-value
  category.
- A big chunk of the catalog barely sells. 59% of products that sold anything
  at all (19,115 out of 32,216) only sold exactly once in the whole ~2 years.
  Most of the revenue is coming from a much smaller set of repeat sellers.
- There's a clear seasonal spike - November 2017 revenue jumped 52% (Black
  Friday), then dropped 27% the next month. Pretty typical boom-bust pattern
  around a big sales event.

## Folder layout

```
sql/                  the queries
python/               script that runs the analysis + exports CSVs
data/processed/       CSVs the dashboard reads from
data/README.md        where to get the raw dataset
powerbi/              dashboard file (.pbix) + screenshot
```
