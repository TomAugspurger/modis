import json
import os.path
import shutil
import unittest
from tempfile import TemporaryDirectory

import pytest
from pystac import CatalogType, MediaType

import stactools.modis.stac
from stactools.modis.file import File

from . import test_data

directory = test_data.get_path("data-files")
args = []
ids = []
for file_name in os.listdir(directory):
    if os.path.splitext(file_name)[1] != ".xml":
        continue
    file = File(os.path.join(directory, file_name))
    collection_path = os.path.join(directory, "expected", file.product,
                                   file.version, "collection.json")
    item_path = os.path.join(directory, "expected", file.product, file.version,
                             file.id, f"{file.id}.json")
    args.append((file.href, collection_path, item_path))
    ids.append(file.product)

cog_product = "MCD12Q1"
cog_version = "006"


@pytest.mark.parametrize("metadata_path,collection_path,item_path",
                         args,
                         ids=ids)
def test_metadata_files(metadata_path: str, collection_path: str,
                        item_path: str) -> None:
    """Compares creates STAC Collections and Items to expected values (located
    in tests/data-files/expected.

    If you change the logic in the STAC object creation, or you add new
    products, run `scripts/create_expected.py` to regenerate the expected STAC
    objects.
    """
    test_case = unittest.TestCase()
    test_case.maxDiff = None
    with open(collection_path) as file:
        expected_collection_dict = json.load(file)
    with open(item_path) as file:
        expected_item_dict = json.load(file)

    modis_file = File(metadata_path)
    collection = stactools.modis.stac.create_collection(
        modis_file.product, modis_file.version)
    with TemporaryDirectory() as temporary_directory:
        temporary_metadata_path = os.path.join(temporary_directory,
                                               os.path.basename(metadata_path))
        temporary_file = File(temporary_metadata_path)
        expected_directory = os.path.join(temporary_directory, "expected",
                                          modis_file.product,
                                          modis_file.version)
        collection.set_self_href(
            os.path.join(expected_directory, "collection.json"))
        shutil.copyfile(modis_file.xml_href, temporary_file.xml_href)
        if os.path.exists(modis_file.hdf_href):
            shutil.copyfile(modis_file.hdf_href, temporary_file.hdf_href)

        if temporary_file.product == cog_product and temporary_file.version == cog_version:
            cog_directory = temporary_directory
            create_cogs = True
        else:
            cog_directory = None
            create_cogs = False
        item = stactools.modis.stac.create_item(temporary_metadata_path,
                                                cog_directory=cog_directory,
                                                create_cogs=create_cogs)
        collection.add_item(item)
        collection.make_all_asset_hrefs_relative()
        collection.save(catalog_type=CatalogType.SELF_CONTAINED)

        with open(collection.self_href) as file:
            collection_dict = json.load(file)
        test_case.assertDictEqual(collection_dict, expected_collection_dict)

        with open(os.path.join(expected_directory, item.id,
                               f"{item.id}.json")) as file:
            item_dict = json.load(file)
        test_case.assertDictEqual(item_dict, expected_item_dict)


def test_collection_id() -> None:
    assert stactools.modis.stac.collection_id(
        "product", "version") == "modis-product-version"


def test_read_href_modifier() -> None:
    href = test_data.get_path(
        "data-files/MCD12Q1.A2001001.h00v08.006.2018142182903.hdf.xml")

    did_it = False

    def read_href_modifier(href: str) -> str:
        nonlocal did_it
        did_it = True
        return href

    _ = stactools.modis.stac.create_item(href,
                                         read_href_modifier=read_href_modifier)
    assert did_it


def test_cog_directory() -> None:
    href = test_data.get_path(
        "data-files/MCD12Q1.A2001001.h00v08.006.2018142182903.hdf.xml")
    item = stactools.modis.stac.create_item(
        href, cog_directory=os.path.dirname(href))

    cog_assets = [
        asset for asset in item.assets.values()
        if asset.media_type == MediaType.COG
    ]
    assert len(cog_assets) == 13
