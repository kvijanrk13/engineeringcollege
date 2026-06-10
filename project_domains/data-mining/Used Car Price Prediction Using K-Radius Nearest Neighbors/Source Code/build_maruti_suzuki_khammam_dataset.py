from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
DATASETS_DIR = PROJECT_DIR.parent / "datasets"
INPUT_DIR = DATASETS_DIR / "vehicle-dataset-from-cardekho"
OUTPUT_FILE = DATASETS_DIR / "maruti_suzuki_khammam.csv"

SOURCE_FILES = [
    INPUT_DIR / "car details v4.csv",
    INPUT_DIR / "Car details v3.csv",
    INPUT_DIR / "CAR DETAILS FROM CAR DEKHO.csv",
]

SELECTED_COLUMNS = [
    "Make",
    "Model",
    "Year",
    "Price",
    "Kilometer",
    "Fuel Type",
    "Transmission",
    "Location",
]


def load_source_dataframe() -> pd.DataFrame:
    for path in SOURCE_FILES:
        if path.exists():
            return pd.read_csv(path)
    raise FileNotFoundError(
        "No Cardekho source file found. Expected one of: "
        + ", ".join(str(p.name) for p in SOURCE_FILES)
    )


def normalize_location(value: str) -> tuple[str, str, str]:
    text = str(value or "").strip()
    city = ""
    district = ""
    state = ""
    if text:
        city = text
        if "hyderabad" in text.lower() or "secunderabad" in text.lower() or "telangana" in text.lower():
            state = "Telangana"
        if "khammam" in text.lower():
            district = "Khammam"
    return city, district, state


def build_dataset() -> pd.DataFrame:
    raw = load_source_dataframe()
    df = raw.copy()

    df = df[df["Make"].astype(str).str.contains("Maruti", case=False, na=False)]
    df = df[df["Year"].astype(float) >= 2015]

    result = pd.DataFrame(
        {
            "make": df["Make"].astype(str).str.strip(),
            "model": df["Model"].astype(str).str.strip(),
            "year": df["Year"].astype(int),
            "price_inr": pd.to_numeric(df["Price"], errors="coerce"),
            "on_road_price_inr": pd.to_numeric(df["Price"], errors="coerce"),
            "fuel_type": df["Fuel Type"].astype(str).str.strip(),
            "transmission": df["Transmission"].astype(str).str.strip(),
            "km_driven": df["Kilometer"].astype(str).str.replace(",", "", regex=False),
            "location": df["Location"].astype(str).str.strip(),
            "city": "",
            "district": "",
            "state": "",
            "image_url": "",
            "source_url": "",
            "notes": "",
        }
    )

    result[["city", "district", "state"]] = result["location"].apply(
        lambda value: pd.Series(normalize_location(value))
    )

    result["location"] = result["location"].replace("nan", "", regex=False)
    return result


def main() -> None:
    output = build_dataset()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_FILE, index=False)
    print(f"Wrote {len(output):,} Maruti Suzuki rows to {OUTPUT_FILE}")
    print(output.head().to_string(index=False))


if __name__ == "__main__":
    main()
