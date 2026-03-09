import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from pathlib import Path

# PROJECT PATHS

PROJECT_ROOT = Path.cwd().parents[1]

RAW_DATA = PROJECT_ROOT / "data" / "raw-data"
DERIVED_DATA = PROJECT_ROOT / "data" / "derived-data"

DERIVED_DATA.mkdir(parents=True, exist_ok=True)

# LOAD 2023 WARD BOUNDARIES

wards = gpd.read_file(
    RAW_DATA / "wards_2023_with_2024_foreclosures.geojson"
)

wards = wards.to_crs(epsg=4326)

# ensure ward column is numeric
wards["ward"] = wards["ward"].astype(int)

# LOAD VACANT PARCEL DATA

vacant = pd.read_csv(
    RAW_DATA / "vacant_minimal.csv"
)

vacant["latitude"] = vacant["latitude"].astype(float)
vacant["longitude"] = vacant["longitude"].astype(float)

geometry = [Point(xy) for xy in zip(vacant["longitude"], vacant["latitude"])]

vacant_gdf = gpd.GeoDataFrame(
    vacant,
    geometry=geometry,
    crs="EPSG:4326"
)

# SPATIAL JOIN VACANT → WARD

vacant_joined = gpd.sjoin(
    vacant_gdf,
    wards[["ward", "geometry"]],
    how="left",
    predicate="within"
)

# rename ward column from join
vacant_joined = vacant_joined.rename(columns={"ward": "ward_spatial"})

# remove duplicate columns created by sjoin
vacant_joined = vacant_joined.loc[:, ~vacant_joined.columns.duplicated()]

# remove spatial join index column if present
if "index_right" in vacant_joined.columns:
    vacant_joined = vacant_joined.drop(columns=["index_right"])

# AGGREGATE VACANT COUNT BY WARD

vacant_by_ward = (
    vacant_joined
    .groupby("ward_spatial")
    .size()
    .reset_index(name="vacant_count")
)

# LOAD FORECLOSURE RATE (2024)

foreclosures = pd.read_csv(
    RAW_DATA / "foreclosures_chicago_wards_clean.csv"
)

foreclosures["ward"] = (
    foreclosures["Geography"]
    .str.replace("Ward ", "", regex=False)
    .astype(int)
)

foreclosures_2024 = (
    foreclosures[["ward", "2024"]]
    .rename(columns={"2024": "foreclosure_rate_2024"})
)

# MERGE EVERYTHING INTO WARDS

wards = wards.merge(
    vacant_by_ward,
    left_on="ward",
    right_on="ward_spatial",
    how="left"
)

wards = wards.merge(
    foreclosures_2024,
    on="ward",
    how="left"
)

# fill missing values
wards["vacant_count"] = wards["vacant_count"].fillna(0)
wards["foreclosure_rate_2024"] = wards["foreclosure_rate_2024"].fillna(0)


# BUILD HOUSING DISTRESS INDEX


# normalize foreclosure rate
wards["foreclosure_norm"] = (
    (wards["foreclosure_rate_2024"] - wards["foreclosure_rate_2024"].min()) /
    (wards["foreclosure_rate_2024"].max() - wards["foreclosure_rate_2024"].min())
)

# normalize vacancy
wards["vacancy_norm"] = (
    (wards["vacant_count"] - wards["vacant_count"].min()) /
    (wards["vacant_count"].max() - wards["vacant_count"].min())
)

#COMPOSITE INDEX
wards["housing_distress_index"] = (
    wards["foreclosure_norm"] + wards["vacancy_norm"]
) / 2

#CREATE RISK TIERS
wards["risk_tier"] = pd.qcut(
    wards["housing_distress_index"],
    q=3,
    labels=["Low", "Watch", "Critical"]
)


# SAVE FINAL DASHBOARD FILES

wards.to_file(
    DERIVED_DATA / "wards_2023_final_dashboard.geojson",
    driver="GeoJSON"
)

vacant_joined.to_file(
    DERIVED_DATA / "vacant_with_ward_2023.geojson",
    driver="GeoJSON"
)

print("Processing complete. Files exported.")