import argparse
import logging
from pathlib import Path
from typing import Optional

from image_2_excel.image_2_excel import (
    get_random_cat_image,
    image_to_horizontal_pixel_array,
    pixel_array_to_excel,
    resize_image,
)


CLI_LOGGER = "image_2_excel_cli"


def parse_config():
    parser = argparse.ArgumentParser(description="Turn images into excel files.")
    parser.add_argument("--input", "-i", type=Path, help="Input image path")
    parser.add_argument("--output", "-o", type=Path, help="Output path")
    parser.add_argument(
        "--dimensions",
        "-d",
        type=int,
        nargs=2,
        default=[128, 256],
        help="Rescale image dimensions, in excel this will be 3*x_dim*y_dim cells total",
    )
    parser.add_argument(
        "--save-resized-image",
        action=argparse.BooleanOptionalAction,
        help="Save the rescaled image to the output folder",
    )
    parser.add_argument(
        "--cat",
        action=argparse.BooleanOptionalAction,
        help="If no input is provided will download a random cat image to use",
    )
    parser.add_argument("-v", "--verbose", action="count", default=0)
    return parser


def handle_filepaths(args):
    if args.input:
        image_filepath = Path(args.input)
    elif args.cat:
        print("Saving a random cat image from the web :^)")
        image_filepath = get_random_cat_image("random_cat")
    else:
        raise Exception("An input path is required if not using the --cat flag.")

    if args.output:
        output_filepath = Path(args.output).with_suffix(".xlsx")
    else:
        output_filepath = Path("./image_to_excel_export.xlsx")

    if args.save_resized_image:
        resized_image_path = Path(output_filepath).parent.joinpath(
            "./resized_image.jpg"
        ) or Path("./resized_image.jpg")
    else:
        resized_image_path = None

    return image_filepath, resized_image_path, output_filepath


def set_console_logger(name, verbose: int = 0):
    logger = logging.getLogger(name)

    c_handler = logging.StreamHandler()
    c_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    logger.propagate = False

    if verbose >= 2:
        logger.setLevel("DEBUG")
    elif verbose == 1:
        logger.setLevel("INFO")
    else:
        logger.setLevel("WARNING")

    return logger


def handle_image_dimensions(dimensions: Optional[list[int]] = None) -> tuple[int, int]:
    if dimensions:
        x, y = dimensions
        return (x, y)
    return (128, 256)


def main():
    parser = parse_config()
    args = parser.parse_args()

    log = set_console_logger(CLI_LOGGER, args.verbose)
    log.debug(f"{args=}")

    image_filepath, resized_image_path, output_filepath = handle_filepaths(args)

    log.debug("Resizing Image")
    dimensions = handle_image_dimensions(args.dimensions)
    resized_image = resize_image(
        image_filepath, output_path=resized_image_path, dimensions=dimensions
    )
    log.debug("Converting Image to Excel File")
    pixel_array = image_to_horizontal_pixel_array(resized_image)
    pixel_array_to_excel(pixel_array, output_filepath)
