from flask import Blueprint
import tempfile
from io import BytesIO
from flask_socketio import emit
from tqdm import tqdm
from .. import socketio

extract_bp = Blueprint('extract_bp', __name__)

def extract_text_from_txt(file, lines_per_page=50, update_progress=None):
    text = file.read().decode('utf-8')
    lines = text.split('\n')
    total_lines = len(lines)
    texts = {}
    
    for i in range(0, len(lines), lines_per_page):
        page_number = (i // lines_per_page) + 1
        page_text = '\n'.join(lines[i:i + lines_per_page])
        texts[f'page {page_number}'] = page_text

        # Update progress
        if update_progress:
            update_progress(i + lines_per_page, total_lines)

    # Ensure the final progress update marks completion
    if update_progress:
        update_progress(total_lines, total_lines)

    return texts

import pdfplumber
import fitz  # PyMuPDF
from io import BytesIO

def extract_text_from_pdf(file, update_progress=None):
    with pdfplumber.open(file) as pdf:
        total_pages = len(pdf.pages)
        texts = {}
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or "No extractable text on this page."
            texts[f'page {i + 1}'] = text
            if update_progress:
                update_progress(i + 1, total_pages)  # Update progress
    return texts

def extract_cover_image_from_pdf(file):
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    if pdf_document.page_count > 0:
        first_page = pdf_document.load_page(0)  # Load the first page
        image_list = first_page.get_images(full=True)
        if image_list:
            xref = image_list[0][0]  # Extract the first image from the list
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_stream = BytesIO(image_bytes)
            return image_stream
    return None

def extract_pdf_metadata(file):
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    metadata = pdf_document.metadata
    authors = metadata.get("author", "Unknown Author").split(", ")
    
    return {
        "title": metadata.get("title", "Unknown Title"),
        "authors": authors,
        "subject": metadata.get("subject", "Unknown Subject"),
        "keywords": metadata.get("keywords", "Unknown Keywords"),
    }

from ebooklib import epub
import ebooklib
from bs4 import BeautifulSoup

def extract_text_from_epub(file, update_progress=None):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        file.save(tmp_file.name)
        tmp_file_path = tmp_file.name

    book = epub.read_epub(tmp_file_path)
    texts = {}
    section_count = 0
    total_sections = len(list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT)))

    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        section_count += 1
        content = item.get_body_content().decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        texts[f'page {section_count}'] = text
        if update_progress:
            update_progress(section_count, total_sections)  # Update progress

    # Ensure the final progress update marks completion
    if update_progress:
        update_progress(total_sections, total_sections)

    return texts

def extract_cover_image_from_epub(file):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        file.save(tmp_file.name)
        tmp_file_path = tmp_file.name

    book = epub.read_epub(tmp_file_path)
    for item in book.get_items_of_type(ebooklib.ITEM_IMAGE):
        image_bytes = item.get_content()
        image_stream = BytesIO(image_bytes)
        return image_stream
    return None

def extract_epub_metadata(file):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        file.save(tmp_file.name)
        tmp_file_path = tmp_file.name

    book = epub.read_epub(tmp_file_path)
    metadata = book.get_metadata('DC', 'title')[0][0]

    authors = book.get_metadata('DC', 'creator')
    authors_list = [author[0] for author in authors]

    return {
        "title": metadata,
        "authors": authors_list,
        "subject": book.get_metadata('DC', 'subject'),
        "keywords": book.get_metadata('DC', 'description'),
    }

import mobi
import tempfile
import struct

def extract_text_from_mobi(file, lines_per_page=50, update_progress=None):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        file.save(tmp_file.name)
        tmp_file_path = tmp_file.name

    book = mobi.Mobi(tmp_file_path)
    book.parse()

    text = ''
    for record in book.records:
        if record.type == mobi.Mobi.HEADER:
            continue
        elif record.type == mobi.Mobi.TEXT:
            text += record.data.decode('utf-8')

    lines = text.split('\n')
    texts = {}
    total_lines = len(lines)

    for i in range(0, len(lines), lines_per_page):
        page_number = (i // lines_per_page) + 1
        page_text = '\n'.join(lines[i:i + lines_per_page])
        texts[f'page {page_number}'] = page_text

        # Update progress
        if update_progress:
            update_progress(i + lines_per_page, total_lines)

    # Ensure the final progress update marks completion
    if update_progress:
        update_progress(total_lines, total_lines)

    return texts

def extract_cover_image_from_mobi(file):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        file.save(tmp_file.name)
        tmp_file_path = tmp_file.name

    book = mobi.Mobi(tmp_file_path)
    book.parse()

    if book.cover_offset:
        start = book.cover_offset
        size = struct.unpack_from('>I', book.read_record(0), start)[0]
        cover_data = book.read_record(0)[start + 4: start + 4 + size]
        image_stream = BytesIO(cover_data)
        return image_stream

    return None

def extract_mobi_metadata(file):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        file.save(tmp_file.name)
        tmp_file_path = tmp_file.name

    book = mobi.Mobi(tmp_file_path)
    book.parse()

    metadata = {}
    if book.exth:
        metadata = {
            "title": book.title,
            "authors": [author.strip() for author in book.authors.split(';')],
            "subject": book.subject,
            "keywords": book.tags
        }
    
    return metadata
