import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from pathlib import Path

# Project paths
# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA = PROJECT_ROOT / "data" / "raw-data"
DERIVED_DATA = PROJECT_ROOT / "data" / "derived-data"

DERIVED_DATA.mkdir(parents=True, exist_ok=True)

# Load ward boundaries
wards = gpd.read_file(RAW_DATA / "wards_2023_with_2024_foreclosures.geojson")
wards = wards.to_crs(epsg=4326)
wards["ward"] = wards["ward"].astype(int)

# Load vacant parcel dataset
vacant = pd.read_csv(RAW_DATA / "vacant_minimal.csv")
vacant["latitude"] = vacant["latitude"].astype(float)
vacant["longitude"] = vacant["longitude"].astype(float)

# Convert parcels to spatial points
geometry = [Point(xy) for xy in zip(vacant["longitude"], vacant["latitude"])]
vacant_gdf = gpd.GeoDataFrame(vacant, geometry=geometry, crs="EPSG:4326")

# Spatial join parcels to wards
vacant_joined = gpd.sjoin(
    vacant_gdf,
    wards[["ward", "geometry"]],
    how="left",
    predicate="within"
)

vacant_joined = vacant_joined.rename(columns={"ward": "ward_spatial"})
vacant_joined = vacant_joined.loc[:, ~vacant_joined.columns.duplicated()]

if "index_right" in vacant_joined.columns:
    vacant_joined = vacant_joined.drop(columns=["index_right"])

# Count vacant parcels per ward
vacant_by_ward = (
    vacant_joined
    .groupby("ward_spatial")
    .size()
    .reset_index(name="vacant_count")
)

# Load foreclosure data
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

# Merge vacancy and foreclosure data with wards
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

wards["vacant_count"] = wards["vacant_count"].fillna(0)
wards["foreclosure_rate_2024"] = wards["foreclosure_rate_2024"].fillna(0)

# Build housing distress index
wards["foreclosure_norm"] = (
    (wards["foreclosure_rate_2024"] - wards["foreclosure_rate_2024"].min()) /
    (wards["foreclosure_rate_2024"].max() - wards["foreclosure_rate_2024"].min())
)

wards["vacancy_norm"] = (
    (wards["vacant_count"] - wards["vacant_count"].min()) /
    (wards["vacant_count"].max() - wards["vacant_count"].min())
)

wards["housing_distress_index"] = (
    wards["foreclosure_norm"] + wards["vacancy_norm"]
) / 2

# Create risk tiers
wards["risk_tier"] = pd.qcut(
    wards["housing_distress_index"],
    q=3,
    labels=["Low", "Watch", "Critical"]
)

# Save ward-level dataset for dashboard
wards.to_file(
    DERIVED_DATA / "wards_2023_final_dashboard.geojson",
    driver="GeoJSON"
)

# Save parcel-level spatial dataset
vacant_joined.to_file(
    DERIVED_DATA / "vacant_with_ward_2023.geojson",
    driver="GeoJSON"
)

# Create lightweight parcel dataset for dashboard dots
vacant_minimal = vacant_joined[["ward_spatial", "geometry"]].copy()

vacant_minimal["longitude"] = vacant_minimal.geometry.x
vacant_minimal["latitude"] = vacant_minimal.geometry.y

vacant_minimal = vacant_minimal.drop(columns="geometry")

vacant_minimal.to_csv(
    DERIVED_DATA / "vacant_minimal.csv",
    index=False
)

print("Spatial preprocessing complete.")