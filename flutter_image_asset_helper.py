"""
Device pixels are also referred to as physical pixels. Logical pixels are also referred to as device-independent or resolution-independent pixels.

By definition, there are roughly 38 logical pixels per centimeter.

See also:

* https://api.flutter.dev/flutter/dart-ui/FlutterView/devicePixelRatio.html
"""

import shutil
import imghdr
from typing import List
from pathlib import Path

from PIL import Image

LOGICAL_PIXELS_PER_CENTIMETER = 38


def centimeters_to_physical_pixels(centimeters: float, nominal_resolution: float) -> float:
    if not centimeters > 0:
        raise ValueError('"centimeters" must be greater than 0.')
    if not nominal_resolution > 0:
        raise ValueError('"nominal_resolution" must be greater than 0.')

    return centimeters*LOGICAL_PIXELS_PER_CENTIMETER*nominal_resolution


def centimeters_to_physical_pixels_printer(centimeters: float, nominal_resolutions: List[float]) -> None:
    for nominal_resolution in nominal_resolutions:
        print('{:>6.2F}cm {:>4.1F}x should have {:>6.0F}px (physical pixels).'.format(centimeters, nominal_resolution, centimeters_to_physical_pixels(centimeters, nominal_resolution)))


def _get_flutter_image_asset_folder_name_by_nominal_resolution(nominal_resolution: int) -> str:
    return '{:.1F}x'.format(nominal_resolution)


def _get_flutter_image_asset_folder_path(target_folder: Path, nominal_resolution: int) -> Path:
    return target_folder if nominal_resolution == 1 else target_folder.joinpath(_get_flutter_image_asset_folder_name_by_nominal_resolution(nominal_resolution))


def _build_folder(folder: Path, target_nominal_resolutions: List[int], forcibly_rebuild: bool) -> bool:
    """
    Returns:
        `False` if the folder already exists and the `forcibly_rebuild` parameter is `False`. Otherwise returns `True`.
    """
    if folder.exists():
        if not forcibly_rebuild:
            return False
        shutil.rmtree(folder)

    folder.mkdir()

    for nominal_resolution in target_nominal_resolutions:
        if nominal_resolution == 1:
            continue
        folder.joinpath(_get_flutter_image_asset_folder_name_by_nominal_resolution(nominal_resolution)).mkdir()

    return True


def generate_flutter_image_assets(source_folder: Path, target_folder: Path, nominal_resolution_of_source: int, nominal_resolution_target: int, forcibly_rebuild: bool = False, append_preferred_dimension: bool = True) -> bool:
    """
    Returns:
        `False` if the folder already exists and the `forcibly_rebuild` parameter is `False`. Otherwise returns `True`.
    """
    if not isinstance(nominal_resolution_of_source, int):
        raise TypeError('"nominal_resolution_of_source" must be an int.')
    if not nominal_resolution_of_source > 0:
        raise ValueError('"nominal_resolution_of_source" must be greater than 0.')

    if not isinstance(nominal_resolution_target, int):
        raise TypeError('"nominal_resolution_target" must be an int.')
    if not nominal_resolution_target > 0:
        raise ValueError('"nominal_resolution_target" must be greater than 0.')
    if nominal_resolution_target > nominal_resolution_of_source:
        raise ValueError('"nominal_resolution_target" can not be greater than "nominal_resolution_of_source"')

    image_file_paths = [path for path in source_folder.iterdir() if path.is_file() and imghdr.what(path)]
    target_nominal_resolutions = list(range(1, nominal_resolution_target+1))

    if not _build_folder(target_folder, target_nominal_resolutions, forcibly_rebuild):
        return False

    for image_file_path in image_file_paths:
        filename_to_save = image_file_path.name

        with Image.open(image_file_path) as image:
            if append_preferred_dimension:
                filename_suffix = image_file_path.suffix
                filename_without_suffix = image_file_path.name[:-len(filename_suffix)]
                filename_to_save = '{!s}-{:.2F}cmx{:.2F}cm{!s}'.format(filename_without_suffix, *map(lambda x: x/nominal_resolution_of_source/LOGICAL_PIXELS_PER_CENTIMETER, image.size), filename_suffix)

            for nominal_resolution in target_nominal_resolutions:
                saving_path = _get_flutter_image_asset_folder_path(target_folder, nominal_resolution).joinpath(filename_to_save)

                if nominal_resolution == nominal_resolution_of_source:
                    image.save(saving_path)
                else:
                    # https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.resize
                    resized_image = image.resize(size=tuple(map(lambda x: round(x / nominal_resolution_of_source * nominal_resolution), image.size)), resample=Image.LANCZOS, reducing_gap=6)
                    resized_image.save(saving_path)
                    resized_image.close()

    return True
