from __future__ import annotations

from dataclasses import dataclass


YEARS = list(range(2015, 2027))


@dataclass(frozen=True)
class MarutiModel:
    name: str
    segment: str
    image_url: str
    launch_year: int
    end_year: int | None
    base_price_2015: int | None
    base_price_launch: int | None
    engine: str
    power: str
    mileage: str
    fuel_types: str
    transmission: str
    key_specs: str
    notes: str = ""


MARUTI_MODELS = [
    MarutiModel(
        "Alto 800",
        "Hatchback",
        "https://imgd.aeplcdn.com/310x174/cw/ec/20917/Maruti-Suzuki-Alto-800-Right-Front-Three-Quarter-76783.jpg",
        2015,
        2023,
        315000,
        None,
        "796 cc",
        "47 bhp",
        "22.05 kmpl",
        "Petrol, CNG",
        "Manual",
        "5 seats | 177 L boot | compact city hatchback",
        "Discontinued after BS6 phase updates.",
    ),
    MarutiModel(
        "Alto K10",
        "Hatchback",
        "https://imgd.aeplcdn.com/310x174/n/cw/ec/130591/alto-k10-exterior-right-front-three-quarter-72.jpeg",
        2015,
        None,
        360000,
        None,
        "998 cc",
        "66 bhp",
        "24.39 kmpl",
        "Petrol, CNG",
        "Manual, AMT",
        "5 seats | K10 engine | compact entry hatchback",
    ),
    MarutiModel(
        "S-Presso",
        "Hatchback",
        "https://imgd.aeplcdn.com/310x174/n/cw/ec/40737/s-presso-exterior-right-front-three-quarter-8.jpeg",
        2019,
        None,
        None,
        420000,
        "998 cc",
        "66 bhp",
        "24.12 kmpl",
        "Petrol, CNG",
        "Manual, AMT",
        "5 seats | high seating | mini SUV styling",
    ),
    MarutiModel(
        "Celerio",
        "Hatchback",
        "https://imgd.aeplcdn.com/310x174/n/cw/ec/53695/celerio-exterior-right-front-three-quarter-5.jpeg",
        2015,
        None,
        430000,
        None,
        "998 cc",
        "66 bhp",
        "25.24 kmpl",
        "Petrol, CNG",
        "Manual, AMT",
        "5 seats | 313 L boot | fuel-efficient hatchback",
    ),
    MarutiModel(
        "Wagon R",
        "Hatchback",
        "https://imgd.aeplcdn.com/310x174/n/cw/ec/112947/wagon-r-exterior-right-front-three-quarter-3.jpeg",
        2015,
        None,
        470000,
        None,
        "998 cc / 1197 cc",
        "66-89 bhp",
        "24.35 kmpl",
        "Petrol, CNG",
        "Manual, AMT",
        "5 seats | tall-boy design | practical family hatchback",
    ),
    MarutiModel(
        "Swift",
        "Hatchback",
        "https://imgd.aeplcdn.com/310x174/n/cw/ec/54399/swift-exterior-right-front-three-quarter-64.jpeg",
        2015,
        None,
        550000,
        None,
        "1197 cc",
        "80-89 bhp",
        "22.38-24.8 kmpl",
        "Petrol, CNG",
        "Manual, AMT",
        "5 seats | sporty hatchback | Heartect platform",
    ),
    MarutiModel(
        "Baleno",
        "Premium hatchback",
        "https://imgd.aeplcdn.com/310x174/n/cw/ec/106257/baleno-exterior-right-front-three-quarter-2.jpeg",
        2015,
        None,
        610000,
        None,
        "1197 cc",
        "88 bhp",
        "22.35 kmpl",
        "Petrol, CNG",
        "Manual, AMT",
        "5 seats | NEXA premium hatchback | 318 L boot",
    ),
    MarutiModel(
        "Ignis",
        "Hatchback",
        "https://imgd.aeplcdn.com/310x174/n/cw/ec/40325/ignis-exterior-right-front-three-quarter-2.jpeg",
        2017,
        None,
        None,
        520000,
        "1197 cc",
        "82 bhp",
        "20.89 kmpl",
        "Petrol",
        "Manual, AMT",
        "5 seats | compact NEXA hatchback | urban crossover styling",
    ),
    MarutiModel(
        "Dzire",
        "Compact sedan",
        "https://imgd.aeplcdn.com/310x174/n/cw/ec/45691/dzire-exterior-right-front-three-quarter-3.jpeg",
        2015,
        None,
        620000,
        None,
        "1197 cc",
        "80-89 bhp",
        "23.26-24.79 kmpl",
        "Petrol, CNG",
        "Manual, AMT",
        "5 seats | compact sedan | high mileage family car",
    ),
    MarutiModel(
        "Ciaz",
        "Sedan",
        "https://imgd.aeplcdn.com/310x174/cw/ec/19242/Maruti-Suzuki-Ciaz-Right-Front-Three-Quarter-60066.jpg",
        2015,
        None,
        850000,
        None,
        "1462 cc",
        "103 bhp",
        "20.04 kmpl",
        "Petrol",
        "Manual, Automatic",
        "5 seats | mild-hybrid sedan | spacious cabin",
    ),
    MarutiModel(
        "Vitara Brezza / Brezza",
        "Compact SUV",
        "https://imgd.aeplcdn.com/310x174/n/cw/ec/123185/brezza-exterior-right-front-three-quarter-4.jpeg",
        2016,
        None,
        None,
        820000,
        "1248 cc diesel / 1462 cc petrol",
        "89-102 bhp",
        "17.38-19.8 kmpl",
        "Diesel till 2020, Petrol/CNG later",
        "Manual, Automatic",
        "5 seats | compact SUV | 328 L boot",
    ),
    MarutiModel(
        "Ertiga",
        "MPV",
        "https://imgd.aeplcdn.com/310x174/n/cw/ec/115777/ertiga-exterior-right-front-three-quarter-3.jpeg",
        2015,
        None,
        760000,
        None,
        "1462 cc",
        "102 bhp",
        "20.51 kmpl",
        "Petrol, CNG",
        "Manual, Automatic",
        "7 seats | family MPV | smart-hybrid petrol",
    ),
    MarutiModel(
        "Eeco",
        "Van",
        "https://imgd.aeplcdn.com/310x174/n/cw/ec/40741/eeco-exterior-right-front-three-quarter.jpeg",
        2015,
        None,
        390000,
        None,
        "1197 cc",
        "71-80 bhp",
        "19.71 kmpl",
        "Petrol, CNG",
        "Manual",
        "5/7 seats | passenger and utility van",
    ),
    MarutiModel(
        "S-Cross",
        "Crossover",
        "https://imgd.aeplcdn.com/310x174/cw/ec/17316/Maruti-Suzuki-S-Cross-Right-Front-Three-Quarter-72084.jpg",
        2015,
        2022,
        950000,
        None,
        "1248 cc diesel / 1462 cc petrol",
        "89-103 bhp",
        "18.43 kmpl",
        "Diesel, Petrol",
        "Manual, Automatic",
        "5 seats | NEXA crossover | premium cabin",
        "Replaced in market by newer SUV/crossover models.",
    ),
    MarutiModel(
        "XL6",
        "MPV",
        "https://imgd.aeplcdn.com/310x174/n/cw/ec/42355/xl6-exterior-right-front-three-quarter-12.jpeg",
        2019,
        None,
        None,
        1120000,
        "1462 cc",
        "102 bhp",
        "20.27 kmpl",
        "Petrol, CNG",
        "Manual, Automatic",
        "6 seats | captain seats | premium Ertiga-based MPV",
    ),
    MarutiModel(
        "Fronx",
        "Compact SUV",
        "https://imgd.aeplcdn.com/310x174/n/cw/ec/130591/fronx-exterior-right-front-three-quarter-111.jpeg",
        2023,
        None,
        None,
        780000,
        "998 cc turbo / 1197 cc",
        "89-99 bhp",
        "20.01-22.89 kmpl",
        "Petrol, CNG",
        "Manual, AMT, Automatic",
        "5 seats | NEXA coupe SUV | turbo option",
    ),
    MarutiModel(
        "Grand Vitara",
        "SUV",
        "https://imgd.aeplcdn.com/310x174/n/cw/ec/115601/grand-vitara-exterior-right-front-three-quarter-3.jpeg",
        2022,
        None,
        None,
        1080000,
        "1462 cc mild hybrid / 1490 cc strong hybrid",
        "91-102 bhp",
        "21.11-27.97 kmpl",
        "Petrol, CNG, Hybrid",
        "Manual, Automatic, e-CVT",
        "5 seats | strong-hybrid option | panoramic sunroof variants",
    ),
    MarutiModel(
        "Jimny",
        "Off-road SUV",
        "https://imgd.aeplcdn.com/310x174/n/cw/ec/131849/jimny-exterior-right-front-three-quarter-27.jpeg",
        2023,
        None,
        None,
        1250000,
        "1462 cc",
        "103 bhp",
        "16.94 kmpl",
        "Petrol",
        "Manual, Automatic",
        "4 seats | 4x4 | ladder-frame off-road SUV",
    ),
    MarutiModel(
        "Invicto",
        "Premium MPV",
        "https://imgd.aeplcdn.com/310x174/n/cw/ec/132527/invicto-exterior-right-front-three-quarter-4.jpeg",
        2023,
        None,
        None,
        2550000,
        "1987 cc strong hybrid",
        "184 bhp system output",
        "23.24 kmpl",
        "Hybrid petrol",
        "e-CVT",
        "7/8 seats | premium hybrid MPV | NEXA flagship",
    ),
]


def _starting_price(model: MarutiModel) -> int:
    if model.base_price_2015 is not None:
        return model.base_price_2015
    if model.base_price_launch is not None:
        return model.base_price_launch
    raise ValueError(f"No base price configured for {model.name}")


def approximate_on_road_price(model: MarutiModel, year: int) -> int | None:
    if year < model.launch_year:
        return None
    if model.end_year is not None and year > model.end_year:
        return None

    start_year = 2015 if model.base_price_2015 is not None else model.launch_year
    ex_showroom = _starting_price(model) * (1.045 ** (year - start_year))

    # Telangana on-road price approximation for project display:
    # ex-showroom + road tax/registration + insurance + handling/fastag buffer.
    on_road = ex_showroom * 1.17
    return int(round(on_road, -3))


def format_price(value: int | None) -> str:
    if value is None:
        return "-"
    return f"Rs {value:,.0f}"


def model_year_specs(model: MarutiModel) -> list[dict[str, str | int]]:
    rows = []
    for year in YEARS:
        price = approximate_on_road_price(model, year)
        if price is None:
            status = "Not on sale"
        elif model.end_year == year:
            status = f"Last sale year. {model.notes}".strip()
        else:
            status = model.notes or "Approximate Khammam on-road project estimate"

        rows.append(
            {
                "year": year,
                "price": format_price(price),
                "engine": model.engine if price else "-",
                "power": model.power if price else "-",
                "mileage": model.mileage if price else "-",
                "fuel_types": model.fuel_types if price else "-",
                "transmission": model.transmission if price else "-",
                "status": status,
            }
        )
    return rows


def maruti_project_dataset() -> list[dict]:
    data = []
    for model in MARUTI_MODELS:
        yearly_specs = model_year_specs(model)
        data.append(
            {
                "name": model.name,
                "segment": model.segment,
                "image_url": model.image_url,
                "key_specs": model.key_specs,
                "prices": [row["price"] for row in yearly_specs],
                "yearly_specs": yearly_specs,
            }
        )
    return data
