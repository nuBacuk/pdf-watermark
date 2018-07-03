# pdf-watermark  [![Build Status](https://travis-ci.com/nuBacuk/pdf-watermark.svg?branch=master)](https://travis-ci.com/nuBacuk/pdf-watermark)
Creates watermark in pdf and makes protection from editing.

## Install 
1. apt-get install pdftk python3 python3-pip
2. pip3 install python-magic pypdf2 reportlab

## Use
python3 ./pdf-watermark.py -w 'File owner Ilya Khramtsov'

**-i If the file is not specified, will deliver the watermarks to all pda files in the current directory.**


## Settings at the beginning of the file.
- POSITION = 'bottom-middle'  # Расположение
- pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))  # Название шрифта и название файла шрифта
- FONT_SIZE = 12  # Размер шрифта
- FONT_COLOR = '#cccccc'  # Цвет шрифта
- VALIDATE = 'trustworthy'
- PREFIX = 'my'
- SECURE_NAME = 'TK_'  # Имя файла после установки пароля
- OWNER_PASS = '333'  # Пароль на редактирование
