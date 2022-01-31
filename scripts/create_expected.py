#!/usr/bin/env python3

import os

from pystac import CatalogType

import stactools.modis.stac
from stactools.modis.file import File

data_files_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    "tests", "data-files")
expected_directory = os.path.join(data_files_directory, "expected")

for file_name in os.listdir(data_files_directory):
    if os.path.splitext(file_name)[1] == ".xml":
        file = File(os.path.join(data_files_directory, file_name))
        collection = stactools.modis.stac.create_collection(file.catalog_id)
        collection_path = os.path.join(expected_directory, file.version,
                                       file.product, "collection.json")
        collection.set_self_href(collection_path)

        item_file_name = f"{file.id}.json"
        item = stactools.modis.stac.create_item(file.path)
        item.validate()

        collection.add_item(item)
        collection.save(catalog_type=CatalogType.SELF_CONTAINED)