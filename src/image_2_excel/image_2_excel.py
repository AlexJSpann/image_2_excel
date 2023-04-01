import mimetypes
from pathlib import Path
from typing import Optional

import numpy as np
import requests
import xlsxwriter
from PIL import Image


def get_random_cat_image(image_name: str, output_directory: Path = Path("./")) -> Path:
    cat_api_url = "https://api.thecatapi.com/v1/images/search"

    api_response = requests.get(cat_api_url)
    if api_response.ok:
        data = api_response.json()
        cat_image_url = data[0]["url"]
    else:
        raise Exception(f"Failed Getting Cat URL ")

    cat_response = requests.get(cat_image_url)
    if cat_response.ok:
        content_type = cat_response.headers["content-type"]
        extension = str(mimetypes.guess_extension(content_type))
        with open(image_name + extension, "wb") as fd:
            fd.write(cat_response.content)
    else:
        raise Exception("Failed Getting Cat Image")

    return Path.joinpath(output_directory, Path(image_name).with_suffix(extension))


def resize_image(
    image_path: Path,
    output_path: Optional[Path] = None,
    dimensions: tuple[int, int] = (128, 256),
) -> Image.Image:
    with Image.open(image_path) as image:
        image.thumbnail(dimensions, Image.LANCZOS)
    if output_path:
        image.save(output_path, quality=100)
    return image


def image_to_horizontal_pixel_array(image: Image.Image) -> np.ndarray:
    image_ndarray = np.asarray(image.convert("RGB"))
    # for each RGB pixel split into 3 rows in RGB order
    h_stripe_pixel_array = image_ndarray.transpose((0, 2, 1)).reshape(
        image_ndarray.shape[0] * 3, -1
    )
    return h_stripe_pixel_array


def pixel_array_to_excel(pixel_array: np.ndarray, output_path: Path) -> None:
    Nx, Ny = pixel_array.shape
    color_lookup = {0: "red", 1: "green", 2: "blue"}

    with xlsxwriter.Workbook(output_path) as workbook:
        cell_format = workbook.add_format()
        cell_format.set_font_size(5)

        worksheet = workbook.add_worksheet()
        worksheet.set_default_row(8, hide_unused_rows=True)
        worksheet.set_column(
            0, Ny, width=3, cell_format=cell_format
        )  # Fix column width
        # worksheet.set_default_column(4)

        for row in range(Nx):
            # Conditional format entire row to be R, G or B
            color_scale = {
                "type": "2_color_scale",
                "min_type": "num",
                "max_type": "num",
                "min_value": 0,
                "max_value": 255,
                "min_color": "#000000",
                "max_color": color_lookup[row % 3],
            }
            worksheet.conditional_format(row, 0, row, Ny, color_scale)
            for col in range(Ny):
                worksheet.write_number(row, col, pixel_array[row, col])


def convert_image(
    input_path: Path,
    output_path: Path = Path("./image_to_excel_export.xlsx"),
    dimensions: tuple[int, int] = (128, 256),
) -> None:
    image = resize_image(input_path, dimensions=dimensions)
    pixel_array = image_to_horizontal_pixel_array(image)
    pixel_array_to_excel(pixel_array, output_path)
