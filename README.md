cat > README.md << 'EOF'
# IPL Cricket AI Analytics Platform

## What I am building

This is a personal data engineering project I built to learn modern data engineering and AI tools. I used IPL cricket data as the data source but the techniques and architecture I used are the same as what companies use in banking, healthcare, e-commerce and any other industry.

The goal is to build a complete end to end platform - starting from raw data, cleaning it, storing it in the cloud, analysing it, connecting it to a dashboard and finally training an AI agent that can answer questions from the data in plain English.

## What I am learning

- How to design a data lake architecture (Bronze, Silver, Gold)
- How to clean and transform large datasets
- How to use Apache Spark and PySpark for big data processing
- How to build Delta tables in Databricks
- How to write SQL queries on cloud data
- How to connect data to Power BI for dashboards
- How to build a RAG AI agent using Azure OpenAI
- How to use Git and GitHub for version control

## The architecture

**Bronze** - Raw data exactly as received. Not touched.

**Silver** - Cleaned and standardised data saved as Parquet files.

**Gold** - Aggregated summary tables ready for dashboards and analysis.

## The data

- Source: Cricsheet (free and open source cricket data)
- 1,226 match files covering 2008 to 2026
- 291,574 individual records

## The platform I am building

**Dashboard** - An interactive Power BI dashboard connected to Databricks. Users can filter by season, venue and team and see key stats and patterns.

**Prediction model** - A machine learning model trained on historical data to predict match scores and win probability based on the current match situation.

**AI chat agent** - A RAG agent using Azure OpenAI that lets users ask questions in plain English and get answers from the real data.

## Tools and Technologies

- Python, pandas, PyArrow
- Apache Spark, PySpark
- Databricks (Free Edition)
- Delta Lake
- Azure (in progress)
- Parquet
- Power BI
- LangChain, Azure OpenAI (coming)
- Git, GitHub
- SQL

## Project files

- explore.py - loads raw data and explores the structure
- clean.py - cleans data and saves as Parquet
- profile.py - automated data quality checks
- analysis.py - analysis and statistics
- gold.py - builds summary tables
- notebooks/01_ipl_analysis.ipynb - PySpark analysis in Databricks

## Certifications I am working on

- Databricks Certified Data Engineer Associate - target July 2026
- Microsoft Azure Data Engineer Associate (DP-203) - target 2026

## About me

I am a data engineer with 7 years of experience at Bank of Montreal. I built this project to get hands on experience with modern cloud data engineering and AI tools.

LinkedIn: Ramakrishna Eadara
Email: Ramkyeadara@gmail.com
EOF