# Fragments

Fragments are JSON files that contain constant values that are included into generated STAC items.
For each version+product combination, the following fragments are _required_:

- `collection.json`: A dictionary of constant fields for each collection:
  - `description`
  - `extent`
  - `title`
  - `providers`
  - `links`
- `bands.json`: A list of `eo:bands` to include in both the item-assets on the collection level, and as an extension on the asset level
- `item-properties.json`: A dictionary of constant fields for each item

The original set of fragments was created from the old `constants.py` via `scripts/create_fragments.py`; new fragments can be created by hand.