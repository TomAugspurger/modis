import os.path
from tempfile import TemporaryDirectory
from unittest import TestCase

import pytest
from pystac import MediaType

import stactools.modis.cog
import stactools.modis.stac
from tests import EXTERNAL_DATA_FILE_NAMES, test_data

SUBDATASET_NAMES = ["Eight_Day_Snow_Cover", "Maximum_Snow_Extent"]


class CogTest(TestCase):

    def test_add_cogs(self) -> None:
        infile = test_data.get_path(
            "data-files/MOD10A2.A2022033.h09v05.061.2022042050729.hdf")
        item = stactools.modis.stac.create_item(infile)
        paths, subdataset_names = stactools.modis.cog.add_cogs(
            item, os.path.dirname(infile))
        assert set(subdataset_names) == set(SUBDATASET_NAMES)
        assert len(paths) == len(SUBDATASET_NAMES)
        for subdataset_name in SUBDATASET_NAMES:
            asset = item.assets[subdataset_name]
            assert os.path.basename(
                asset.href
            ) == f"MOD10A2.A2022033.h09v05.061.2022042050729_{subdataset_name}.tif"
            assert asset.media_type == MediaType.COG

    def test_add_no_cogs(self) -> None:
        infile = test_data.get_path(
            "data-files/MOD10A2.A2022033.h09v05.061.2022042050729.hdf")
        item = stactools.modis.stac.create_item(infile)
        with pytest.raises(ValueError):
            stactools.modis.cog.add_cogs(item, os.path.dirname(__file__))

    def test_cogify(self) -> None:
        infile = test_data.get_path(
            "data-files/MOD10A2.A2022033.h09v05.061.2022042050729.hdf")
        with TemporaryDirectory() as temporary_directory:
            paths, _ = stactools.modis.cog.cogify(infile, temporary_directory)
            assert all(os.path.exists(path) for path in paths)
        self.assertEqual(len(paths), 2)
        file_names = [os.path.basename(path) for path in paths]
        expected_cog_names = [
            f"MOD10A2.A2022033.h09v05.061.2022042050729_{subdataset_name}.tif"
            for subdataset_name in SUBDATASET_NAMES
        ]
        self.assertEqual(set(file_names), set(expected_cog_names))


@pytest.mark.parametrize("file_name", EXTERNAL_DATA_FILE_NAMES)
@pytest.mark.slow
def test_external_data(file_name: str) -> None:
    infile = test_data.get_external_data(file_name)
    _ = test_data.get_external_data(f"{file_name}.xml")
    with TemporaryDirectory() as temporary_directory:
        item = stactools.modis.stac.create_item(
            infile, create_cogs=True, cog_directory=temporary_directory)
        item.validate()
