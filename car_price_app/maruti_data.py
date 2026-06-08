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
        "https://www.marutisuzuki.com/adobe/assets/urn:aaid:aem:17671701-80a4-42fa-a1f1-b3425350e910/as/TVC-Banner_desktop_2000x1171.jpg?height=1171&width=2000&id=1&preferwebp=true",
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
        "https://www.marutisuzuki.com/adobe/assets/urn:aaid:aem:17671701-80a4-42fa-a1f1-b3425350e910/as/TVC-Banner_desktop_2000x1171.jpg?height=1171&width=2000&id=1&preferwebp=true",
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
        "https://www.marutisuzuki.com/adobe/assets/urn:aaid:aem:daf91fb5-29d8-4979-8482-a6c79033c70b/as/Centre_Desktop.png?height=1080&width=1920",
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
        "https://www.marutisuzuki.com/adobe/assets/urn:aaid:aem:ed83cc03-2b30-4383-ba46-b52ca89fc2df/as/Variant-Banner-TVC-2000-1171.png?width=2000&id=1&preferwebp=true",
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
        "https://www.marutisuzuki.com/adobe/assets/urn:aaid:aem:e4d500dc-a6ea-458f-8940-867a1ae4a10e/as/wagenr_TVC-Banner_2000x1171.jpg?height=1171&width=2000&id=1&preferwebp=true",
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
        "https://www.marutisuzuki.com/js/arenabrandjs/threesixtyjs/img/RED/SUZUKI_SWIFT_EXT_360_RED_V-1_1.webp",
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
        "https://www.nexaexperience.com/adobe/assets/urn:aaid:aem:d1f6c965-1ce7-46c9-b3d5-46cac019f825/as/Baleno_Fold_Desktop_Image.png?width=2000&id=1&preferwebp=true",
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
        "https://www.nexaexperience.com/adobe/assets/urn:aaid:aem:36ff1028-4590-4958-a35c-5952d22c390f/as/Ignis_fold_4k_Desktop_Image.png?width=2000&id=1&preferwebp=true",
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
        "https://www.marutisuzuki.com/adobe/assets/urn:aaid:aem:dcb80bf0-b7be-4ddc-9ba0-1b248acf6654/as/Dzire_TVC_Desktop_Dummy.png?width=2000&id=1&preferwebp=true",
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
        "https://www.nexaexperience.com/default-meta-image.png?width=1200&format=pjpg&optimize=medium",
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
        "https://www.marutisuzuki.com/adobe/assets/urn:aaid:aem:06493d36-fbc0-47d9-8f6e-6eb08a229718/as/Brezza_Desktop_Banner_web.jpg?height=820&width=2000&id=1&preferwebp=true",
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
        "https://www.marutisuzuki.com/adobe/assets/urn:aaid:aem:1ec89dd0-f4fc-4499-9401-1a69459f13e7/as/Desktop-Ertiga-Dual-tone-carousel-image.jpg?height=1440&width=2560",
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
        "https://www.marutisuzuki.com/adobe/assets/urn:aaid:aem:d0ee7111-dcb5-479c-b354-d01b87744c0c/as/Eeco_varient_2000x1117_desktop.png?width=2000&id=1&preferwebp=true",
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
        "https://www.nexaexperience.com/default-meta-image.png?width=1200&format=pjpg&optimize=medium",
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
        "https://www.nexaexperience.com/adobe/assets/urn:aaid:aem:f4a1c81c-8c3a-4a7b-94d3-d407e2d86ac5/as/XL6_Banner_Image_Desktop.png?width=2000&id=1&preferwebp=true",
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
        "https://www.nexaexperience.com/adobe/assets/urn:aaid:aem:cbaaf7a8-eef9-4137-9e91-8e914f6ba4f2/as/fronx_fold_Desktop_Image.png?width=2000&id=1&preferwebp=true",
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
        "https://www.nexaexperience.com/adobe/assets/urn:aaid:aem:15d5ba20-d055-4b82-b8ef-985d685e9a8a/as/GV-Desktop-Banner.jpg?height=2160&width=2000&id=1&preferwebp=true",
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
        "https://www.nexaexperience.com/adobe/assets/urn:aaid:aem:5716197a-a15e-424a-ad05-52b52dada745/as/JIMNY_fold_desktop_image.png?width=2000&id=1&preferwebp=true",
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
        "https://www.nexaexperience.com/adobe/assets/urn:aaid:aem:93db3aba-c00e-45a0-b973-12cfe59f25d9/as/Invicto_Banner_Image.png?width=2000&id=1&preferwebp=true",
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
