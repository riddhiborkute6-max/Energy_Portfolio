# Energy Portfolio

Interactive Streamlit portfolio built alongside my TU Berlin Master's thesis, *"From Cannibalization to Opportunity: Quantifying the Value of Industrial Flexibility Assets Under Increasing Renewable Penetration in European Electricity Markets."*

Uses ENTSO-E day-ahead price, wind, and solar data for Germany, the Netherlands, and Denmark (2018-2024) to explore how renewable penetration erodes capture prices, and what that erosion is worth to flexible assets like batteries and demand response.

**Live app:** https://riddhiborkute.streamlit.app/

## Pages

- **Cannibalization Explorer** — capture-price ratios vs. renewable penetration, by market and year
- **Negative Price Heatmap** — sub-zero price hours mapped across hour-of-day and month
- **Flexibility Simulator** — battery storage and demand-response revenue under threshold and daily-arbitrage dispatch strategies
- **Thesis Lab** — research question, methodology, and key literature
- **Research Notes** — running notes on data sources and analytical decisions
- **Price Duration Curves** — annual price distributions by market
- **About** — background and contact

## Stack

Python · Streamlit · Pandas · Plotly · Parquet (ENTSO-E data)

## Run locally

```bash
pip install -r requirements.txt
streamlit run Home.py
```
