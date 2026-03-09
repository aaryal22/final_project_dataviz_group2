# final_project_dataviz_group2


## Data Sources

Several datasets exceed GitHub's 100MB file size limit and are hosted externally. Download each file and place it in `dataset/raw/` before running any code.

| Dataset | Source | Access |
|---|---|---|
| Chicago Outstanding Debt (365+ Days) | Chicago Dept. of Water Management | [Download](https://docs.google.com/spreadsheets/d/11rmLkfwTM4J62-yavqgpoTUvKEGKAFVI/edit?usp=drive_link&ouid=103252786202124037419&rtpof=true&sd=true) |
| Chicago Demolition Permits | Chicago Data Portal | [Download](https://drive.google.com/file/d/1R-_NtNpnVFif8eztaej20XMxue5Dhdb8/view?usp=drive_link) |
| Cook County Parcel Universe | Cook County Assessor's Office | [Download](https://datacatalog.cookcountyil.gov/Property-Taxation/Assessor-Parcel-Universe-Current-Year-Only-/pabr-t5kh/about_data) |
| Chicago Vacant Land Parcels | Cook County Assessor's Office | [Download](https://drive.google.com/file/d/1G8XQ3b05Bop3aKWlFnMmdBDZsP0-rXJ-/view?usp=drive_link), [classcode guide](https://prodassets.cookcountyassessoril.gov/s3fs-public/form_documents/classcode.pdf)|

> **Note:** Files should be saved to `dataset/raw/` without renaming. File paths in `preprocessing.py` are set up accordingly.

## Streamlit App

The interactive dashboard is deployed at: [https://wardleveldebt.streamlit.app]

## Repository Structure

```
├── dataset/
│   ├── raw/          # Original unmodified source files
│   └── cleaned/      # Processed outputs from preprocessing.py
├── streamlit-app/    # Dashboard code and dependencies
├── preprocessing.py  # Data wrangling and index computation
├── final_project.qmd # Writeup source file
└── README.md
```
