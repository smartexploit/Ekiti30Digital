# Ekiti State LGAs Geographic Dataset

This folder contains the initial geographic dataset for the 16 Local Government Areas of Ekiti State.

## Purpose

The dataset supports the Explore Ekiti map and other geographic features of EKITI@30 DIGITAL.

## Available Formats

- `ekiti_lgas.csv` — primary editable dataset
- `ekiti_lgas.json` — structured application data
- `ekiti_lgas.geojson` — map-ready point features

All three formats should contain the same 16 LGA records and remain synchronized after every correction.

## Data Included

Each LGA record contains:

- LGA name
- Headquarters
- Approximate headquarters coordinates
- Major towns and communities
- Notable places
- Important institutions
- Source information
- Source date and last-checked date
- Verification status
- Limitations
- Contributor

## Coordinate Standard

Coordinates use decimal degrees in the WGS84 coordinate system.

The coordinates are approximate town-centre reference points for the respective LGA headquarters. They are not official LGA boundaries, surveyed administrative coordinates, or precise locations of government secretariats.

The point coordinates are suitable for the initial Explore Ekiti map, but they must remain marked as approximate until independently checked against reliable geographic or official records.

## Source Policy

Government publications and official institutional websites are preferred for LGA names, headquarters, institutions, and administrative information.

Secondary geographic databases may support coordinate research, but they should not be treated as the sole authoritative source for administrative facts.

Wikipedia or another general reference may only be recorded as a secondary supporting source. It must not serve as the sole basis for marking a record as verified.

Conflicting information must be documented in the `limitations` field instead of being silently resolved.

## Naming Note

The dataset uses `Aiyekire` as the official LGA name. `Gbonyin` may appear in older or alternative references, so this naming difference is documented in the dataset limitations and source information.

## Verification Status

- `Pending`: Information has been collected but has not completed the required checks.
- `Reviewed`: The information and cited sources have been checked by a contributor or reviewer, but final independent approval is still required.
- `Verified`: The record has passed the project's required independent review and has been approved for publication as verified project knowledge.

A record must not move directly from `Pending` to `Verified` without the required independent review.

## Unresolved Information

Fields marked `To be researched` are intentionally unresolved. They must remain that way until reliable supporting information is found.

Contributors should not fill unresolved fields using assumptions or unsupported claims.

## Limitations

Some coordinates, communities, institutions, landmarks, and administrative details remain provisional.

The inclusion of an institution or place does not mean that its exact coordinates or current operational status have been independently verified.

All records currently marked `Pending` require further review before publication as verified information.

## Contributor

Akintade Daniel Emmanuel  
Geospatial and LGA Lead  
Issue #5
