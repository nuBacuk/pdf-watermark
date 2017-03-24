# -*- coding: utf-8 -*-
# !/usr/bin/env python3
 
import argparse
import PyPDF2
import magic
import mimetypes
import os, sys, io, subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# settings
POSITION = 'bottom-middle'  # Расположение
pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))  # Название шрифта и название файла шрифта
FONT_SIZE = 12  # Размер шрифта
FONT_COLOR = '#cccccc'  # Цвет шрифта
VALIDATE = 'trustworthy'
PREFIX = 'my'
SECURE_NAME = 'TK_'  # Имя файла после установки пароля
OWNER_PASS = '333'  # Пароль на редактирование

 
def is_pdf(path, check):
    if check == 'lazy':
        return is_pad_lazy(path)
    else:
        return is_pdf_trustworthy(path)
 
 
def is_pdf_lazy(path):
    mime_type = mimetypes.guess_type(path)
    if mime_type[0] and mime_type[0] == "application/pdf":
        return True
    return False
 
 
def is_pdf_trustworthy(path):
    if is_pdf_lazy(path):
        if 'PDF' in magic.from_file(path):
            return True
    return False
 
 
def make_list_pdfs_by(path, validate, recursive=False):
    pdfs = []
    for rootdir, dirs, filenames in os.walk(path):
        full_filenames = [os.path.join(rootdir, filename) for filename in filenames]
        pdfs.extend([full_filename for full_filename in full_filenames if is_pdf(full_filename, validate)])
        if not recursive:
            break
    return pdfs
 
 
def make_overlay_pdf(watermark, position, font, fontsize, mediabox):
    lowerLeft = (mediabox.lowerLeft[0].as_numeric(), mediabox.lowerLeft[1].as_numeric())
    lowerRight = (mediabox.lowerRight[0].as_numeric(), mediabox.lowerRight[1].as_numeric())
    upperLeft = (mediabox.upperLeft[0].as_numeric(), mediabox.upperLeft[1].as_numeric())
    upperRight = (mediabox.upperRight[0].as_numeric(), mediabox.upperRight[1].as_numeric())
    width_page = lowerRight[0] - lowerLeft[0]
    height_page = upperLeft[1] - lowerLeft[1]
    margin = {'top': 0.5*cm, 'right': 1*cm, 'bottom': 1*cm, 'left': 1*cm} # margin for top right bottom left in cm
    packet = io.BytesIO()
    canva = canvas.Canvas(packet, pagesize=(width_page, height_page))
    canva.setFont(font, fontsize)
    watermark_width = canva.stringWidth(watermark, font, fontsize)
    canva.setFillColor(HexColor(FONT_COLOR))
    if position == 'top-left':
        x = upperLeft[0] + margin['left']
        y = upperLeft[1] - margin['top'] - fontsize
    elif position == 'top-right':
        x = upperRight[0] - (margin['right'] + watermark_width)
        y = upperRight[1] - margin['top'] - fontsize
    elif position == 'bottom-left':
        x = lowerLeft[0] + margin['left']
        y = lowerLeft[1] + margin['bottom']
    elif position == 'bottom-right':
        x = lowerRight[0] - (margin['right'] + watermark_width)
        y = lowerRight[1] + margin['bottom']
    elif position == 'top-middle':
        x = upperLeft[0] + (upperRight[0]-upperLeft[0])/2.0 - watermark_width/2.0
        y = upperRight[1] - margin['top'] - fontsize
    elif position == 'bottom-middle':
        x = lowerLeft[0] + (lowerRight[0] - lowerLeft[0])/2.0 - watermark_width/2.0
        y = lowerLeft[1] + margin['bottom']
    canva.drawString(x, y, watermark)
    canva.save()
    packet.seek(0)
    return PyPDF2.PdfFileReader(packet)
 
 
def make_watermark(args):
    watermark = args.watermark
    position = args.pos_watermark
    font = args.font
    fontsize = int(args.fontsize)
    for filename in make_list_pdfs_by(args.PDFs, args.validate, args.recursive):
        existing_pdf = PyPDF2.PdfFileReader(open(filename, "rb"))
        i = 0
        while i != existing_pdf.numPages:
            page = existing_pdf.getPage(i)
            overlay_pdf = make_overlay_pdf(watermark, position, font, fontsize, page.mediaBox)
            page.mergePage(overlay_pdf.getPage(0))
            page.mergePage(overlay_pdf.getPage(0))
            i += 1
        output_pdf = PyPDF2.PdfFileWriter()
        output_pdf.appendPagesFromReader(existing_pdf)
        outputStream = open(os.path.join(os.path.dirname(filename), args.prefix+'_'+os.path.basename(filename)), "wb")
        output_pdf.write(outputStream)
        outputStream.close()
        subprocess.call('pdftk %s cat output %s%s encrypt_128bit owner_pw %s' % (args.prefix+'_'+os.path.basename(filename),
                                                                                 SECURE_NAME, filename[2:], OWNER_PASS), shell=True)
        subprocess.call('rm %s' % pdftk_name, shell=True)
        print ("Processing completed for %s" % filename)
        
 
def parse_args():
    parser = argparse.ArgumentParser(usage="%s -w http://forum.ubuntu.ru [-i ~/docs] [-f Times-Roman] "
        "[-s 24] [-p (top-left|top-middle|top-right|bottom-left|bottom-middle|bottom-right)] "
        "[-r] [--prefix your_prefix] [--validate trustworthy]" % (os.path.basename(sys.argv[0])))
    parser.add_argument("-i", "--input", action="store", dest="PDFs", default=".")
    parser.add_argument("-w", "--watermark", action="store", dest="watermark", required=True)
    parser.add_argument("-s", "--font-size", action="store", dest="fontsize", default=FONT_SIZE)
    parser.add_argument("-f", "--font", action="store", dest="font", default="FreeSans")
    parser.add_argument("-p", "--position", action="store", dest="pos_watermark",
        metavar="position watermark", choices=["top-left", "top-middle", "top-right", "bottom-left", "bottom-middle", "bottom-right"], default=POSITION)
    parser.add_argument("-r", "--recursive", action="store_true", dest="recursive", default=False)
    parser.add_argument("--prefix", action="store", dest="prefix", default=PREFIX)
    parser.add_argument("--validate", action="store", dest="validate", choices=['lazy', 'trustworthy'], default=VALIDATE)
    return parser.parse_args()
 
if __name__ == "__main__":
    args = parse_args()
    make_watermark(args)
