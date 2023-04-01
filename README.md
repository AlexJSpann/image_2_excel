# image_2_excel
Simple tool to convert small images to excel documents. Each pixel is split into 3
rows (RGB) and shaded with conditional formatting.

Inspired by [Matt Parker](https://www.youtube.com/watch?v=UBX2QQHlQ_I)

## Installation
```sh
pip install git+https://github.com/TeaFold/image_2_excel
```

## Examples
CLI
```sh
python -m image_2_excel --input my_image.png --output my_spreadsheet.xlsx
```

Importing
```Py
import image_2_excel 
image_2_excel.convert_image("my_image.png", "my_spreadsheet.xlsx")
```
