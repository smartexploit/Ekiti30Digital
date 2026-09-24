import argparse
import json
import re
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from shapely.geometry import shape
from shapely.ops import unary_union


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
}


def normalize(value):
    return re.sub(r"[^a-z0-9]", "", value.lower())


def geometry_parts(geometry):
    if geometry.geom_type == "MultiPolygon":
        return list(geometry.geoms)

    return [geometry]


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

    with urllib.request.urlopen(metadata_url) as response:
        metadata = json.load(response)

    with urllib.request.urlopen(
        metadata["gjDownloadURL"]
    ) as response:
        data = json.load(response)

    ekiti_names = {
        "adoekiti",
        "efon",
        "ekitieast",
        "ekitisouthwest",
        "ekitiwest",
        "emure",
        "aiyekire",
        "gbonyin",
        "idoosi",
        "ijero",
        "ikere",
        "ikole",
        "ilejemeje",
        "irepodunifelodun",
        "iseorun",
        "moba",
        "oye",
    }

    canonical_labels = {
        "adoekiti": "Ado-Ekiti",
        "efon": "Efon",
        "ekitieast": "Ekiti East",
        "ekitisouthwest": "Ekiti South-West",
        "ekitiwest": "Ekiti West",
        "emure": "Emure",
        "aiyekire": "Aiyekire",
        "gbonyin": "Aiyekire",
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

    selected = []

    for feature in data["features"]:
        properties = feature.get("properties", {})

        name = (
            properties.get("shapeName")
            or properties.get("ADM2_NAME")
            or properties.get("admin2Name")
            or properties.get("name")
            or ""
        )

        normalized_name = normalize(name)

        if normalized_name in ekiti_names:
            selected.append({
                "name": name,
                "normalized_name": normalized_name,
                "geometry": shape(feature["geometry"]),
            })

    canonical_found = {
        "aiyekire"
        if item["normalized_name"] == "gbonyin"
        else item["normalized_name"]
        for item in selected
    }

    if len(canonical_found) != 16:
        raise ValueError(
            f"Expected 16 Ekiti LGAs, found "
            f"{len(canonical_found)}"
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
            canonical_labels.get(
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
        f"Ekiti State Local Government Areas\n"
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

    output_path = Path(
        f"02_LGAs/media/{config['folder']}/"
        f"{args.lga}-lga-highlight-map-01.png"
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=180,
        bbox_inches="tight",
        facecolor="white",
    )

    plt.close()

    print("Map generated successfully")
    print("LGA:", title)
    print("Output:", output_path)


if __name__ == "__main__":
    main()