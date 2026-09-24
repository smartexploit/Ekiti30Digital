import argparse
import json
import re
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from shapely.geometry import shape
from shapely.ops import unary_union


# Configuration for all 16 Ekiti State LGAs
LGA_CONFIG = {
    "ado-ekiti": {
        "source_names": {"adoekiti"},
        "title": "Ado-Ekiti",
        "folder": "ado-ekiti",
    },
    "aiyekire": {
        "source_names": {"aiyekire", "gbonyin"},
        "title": "Aiyekire",
        "folder": "aiyekire",
    },
    "efon": {
        "source_names": {"efon"},
        "title": "Efon",
        "folder": "efon",
    },
    "ekiti-east": {
        "source_names": {"ekitieast"},
        "title": "Ekiti East",
        "folder": "ekiti-east",
    },
    "ekiti-south-west": {
        "source_names": {"ekitisouthwest"},
        "title": "Ekiti South-West",
        "folder": "ekiti-south-west",
    },
    "ekiti-west": {
        "source_names": {"ekitiwest"},
        "title": "Ekiti West",
        "folder": "ekiti-west",
    },
    "emure": {
        "source_names": {"emure"},
        "title": "Emure",
        "folder": "emure",
    },
    "ido-osi": {
        "source_names": {"idoosi"},
        "title": "Ido/Osi",
        "folder": "ido-osi",
    },
    "ijero": {
        "source_names": {"ijero"},
        "title": "Ijero",
        "folder": "ijero",
    },
    "ikere": {
        "source_names": {"ikere"},
        "title": "Ikere",
        "folder": "ikere",
    },
    "ikole": {
        "source_names": {"ikole"},
        "title": "Ikole",
        "folder": "ikole",
    },
    "ilejemeje": {
        "source_names": {"ilejemeje"},
        "title": "Ilejemeje",
        "folder": "ilejemeje",
    },
    "irepodun-ifelodun": {
        "source_names": {"irepodunifelodun"},
        "title": "Irepodun/Ifelodun",
        "folder": "irepodun-ifelodun",
    },
    "ise-orun": {
        "source_names": {"iseorun"},
        "title": "Ise/Orun",
        "folder": "ise-orun",
    },
    "moba": {
        "source_names": {"moba"},
        "title": "Moba",
        "folder": "moba",
    },
    "oye": {
        "source_names": {"oye"},
        "title": "Oye",
        "folder": "oye",
    },
}


CANONICAL_LABELS = {
    "adoekiti": "Ado-Ekiti",
    "aiyekire": "Aiyekire",
    "gbonyin": "Aiyekire",
    "efon": "Efon",
    "ekitieast": "Ekiti East",
    "ekitisouthwest": "Ekiti South-West",
    "ekitiwest": "Ekiti West",
    "emure": "Emure",
    "idoosi": "Ido/Osi",
    "ijero": "Ijero",
    "ikere": "Ikere",
    "ikole": "Ikole",
    "ilejemeje": "Ilejemeje",
    "irepodunifelodun": "Irepodun/Ifelodun",
    "iseorun": "Ise/Orun",
    "moba": "Moba",
    "oye": "Oye",
}


EKITI_SOURCE_NAMES = set(CANONICAL_LABELS)


def normalize(value):
    """Convert an LGA name to a simple comparison format."""
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def geometry_parts(geometry):
    """Return the polygons contained in a Polygon or MultiPolygon."""
    if geometry.geom_type == "MultiPolygon":
        return list(geometry.geoms)

    return [geometry]


def get_feature_name(properties):
    """Read the LGA name from supported GeoJSON property fields."""
    return (
        properties.get("shapeName")
        or properties.get("ADM2_NAME")
        or properties.get("admin2Name")
        or properties.get("name")
        or ""
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate an Ekiti State LGA highlight map."
    )

    parser.add_argument(
        "lga",
        choices=sorted(LGA_CONFIG),
        help="LGA folder slug",
    )

    args = parser.parse_args()
    config = LGA_CONFIG[args.lga]

    metadata_url = (
        "https://www.geoboundaries.org/api/current/"
        "gbOpen/NGA/ADM2/"
    )

    print("Downloading geographic boundary information...")

    with urllib.request.urlopen(
        metadata_url,
        timeout=60,
    ) as response:
        metadata = json.load(response)

    geojson_url = metadata["gjDownloadURL"]

    with urllib.request.urlopen(
        geojson_url,
        timeout=120,
    ) as response:
        data = json.load(response)

    selected = []

    for feature in data.get("features", []):
        properties = feature.get("properties", {})
        name = get_feature_name(properties)
        normalized_name = normalize(name)

        if normalized_name in EKITI_SOURCE_NAMES:
            selected.append(
                {
                    "name": name,
                    "normalized_name": normalized_name,
                    "geometry": shape(feature["geometry"]),
                }
            )

    canonical_found = {
        (
            "aiyekire"
            if item["normalized_name"] == "gbonyin"
            else item["normalized_name"]
        )
        for item in selected
    }

    if len(canonical_found) != 16:
        found_names = sorted(canonical_found)

        raise ValueError(
            "Expected 16 Ekiti LGAs, but found "
            f"{len(canonical_found)}: {found_names}"
        )

    highlighted_features = [
        item
        for item in selected
        if item["normalized_name"] in config["source_names"]
    ]

    if not highlighted_features:
        raise ValueError(
            f"Could not find boundary data for {config['title']}."
        )

    state_geometry = unary_union(
        [item["geometry"] for item in selected]
    )

    fig, ax = plt.subplots(figsize=(10, 10))

    for item in selected:
        normalized_name = item["normalized_name"]
        geometry = item["geometry"]

        highlighted = (
            normalized_name in config["source_names"]
        )

        colour = "#15803d" if highlighted else "#d9ead3"

        for polygon in geometry_parts(geometry):
            x, y = polygon.exterior.xy

            ax.fill(
                x,
                y,
                facecolor=colour,
                edgecolor="#ffffff",
                linewidth=1.2,
                zorder=2,
            )

        point = geometry.representative_point()

        ax.text(
            point.x,
            point.y,
            CANONICAL_LABELS.get(
                normalized_name,
                item["name"],
            ),
            fontsize=7,
            ha="center",
            va="center",
            color="#111827",
            zorder=3,
        )

    for polygon in geometry_parts(state_geometry):
        x, y = polygon.exterior.xy

        ax.plot(
            x,
            y,
            color="#14532d",
            linewidth=2.2,
            zorder=4,
        )

    title = config["title"]

    ax.set_title(
        "Ekiti State Local Government Areas\n"
        f"{title} LGA Highlighted",
        fontsize=16,
        fontweight="bold",
        pad=18,
    )

    ax.legend(
        handles=[
            Patch(
                facecolor="#15803d",
                edgecolor="#14532d",
                label=f"{title} LGA",
            ),
            Patch(
                facecolor="#d9ead3",
                edgecolor="#14532d",
                label="Other Ekiti LGAs",
            ),
        ],
        loc="lower left",
        frameon=True,
    )

    ax.text(
        0.5,
        -0.04,
        "Boundary data: geoBoundaries (CC BY 4.0). "
        "Map prepared for EKITI@30 DIGITAL.",
        transform=ax.transAxes,
        ha="center",
        fontsize=8,
        color="#4b5563",
    )

    ax.set_aspect("equal")
    ax.axis("off")

    output_directory = Path(
        "02_LGAs/media"
    ) / config["folder"]

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = output_directory / (
        f"{args.lga}-lga-highlight-map-01.png"
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=180,
        bbox_inches="tight",
        facecolor="white",
    )

    plt.close(fig)

    print("Map generated successfully")
    print("LGA:", title)
    print("Output:", output_path)


if __name__ == "__main__":
    main()