import re
from io import BytesIO

from django.db import migrations
from django.core.files.images import ImageFile
from PIL import Image, ImageDraw, ImageFont


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    text = re.sub(r'_+', '_', text).strip('_')
    return text[:50]


def get_initials(text):
    words = re.findall(r"[A-Za-z0-9]+", text)
    initials = ''.join(w[0].upper() for w in words[:2])
    return initials or 'BK'


def create_placeholder_image(title, category):
    width, height = 200, 280
    img = Image.new('RGB', (width, height), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 28)
        small_font = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    cx, cy = width // 2, 80
    r = 40
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(59, 130, 246), outline=(255, 255, 255), width=3)
    icon = get_initials(title)
    bbox = draw.textbbox((0, 0), icon, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw / 2, cy - th / 2), icon, font=font, fill=(255, 255, 255))
    label = category.upper() if category else 'BOOK'
    bbox = draw.textbbox((0, 0), label, font=small_font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((width / 2 - tw / 2, 150), label, font=small_font, fill=(200, 200, 200))
    title_text = title[:60]
    bbox = draw.textbbox((0, 0), title_text, font=small_font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((width / 2 - tw / 2, 190), title_text, font=small_font, fill=(180, 180, 180))
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return ImageFile(buffer, name=f'book_{slugify(title)}.png')


def normalize(text):
    if not text:
        return ''
    t = text.lower().strip()
    t = re.sub(r'[^a-z0-9\s]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def extract_textbook_ref_entries(book_type, full_text=''):
    text = book_type or full_text or ''
    if not text:
        return [], []
    textbooks = []
    references = []
    parts = text.split('/')
    if len(parts) >= 2:
        text_part = parts[0]
        ref_part = parts[1]
    else:
        text_part = text
        ref_part = ''
    text_entries = re.split(r'[\n]+', text_part)
    for entry in text_entries:
        p = entry.strip()
        if re.match(r'^\d+[\.\)]', p):
            clean = re.sub(r'^\d+[\.\)]\s*', '', p).strip()
            if clean:
                textbooks.append(clean)
    ref_entries = re.split(r'[\n]+', ref_part)
    for entry in ref_entries:
        p = entry.strip()
        if re.match(r'^\d+[\.\)]', p):
            clean = re.sub(r'^\d+[\.\)]\s*', '', p).strip()
            if clean:
                references.append(clean)
    return textbooks, references


def sync_recommendations_to_books(apps, schema_editor):
    Book = apps.get_model('library', 'Book')
    BookRecommendation = apps.get_model('library', 'BookRecommendation')
    Author = apps.get_model('library', 'Author')

    existing_books = {}
    for book in Book.objects.all():
        norm = normalize(book.name)
        if norm:
            existing_books[norm] = book

    for rec in BookRecommendation.objects.all():
        full_text = getattr(rec, 'full_text', '') or ''
        textbooks, references = extract_textbook_ref_entries(rec.book_type, full_text)
        all_entries = [('TEXT', t) for t in textbooks] + [('REFERENCE', r) for r in references]
        if not all_entries:
            continue
        for category, entry_text in all_entries:
            norm = normalize(entry_text)
            if not norm or len(norm) < 3:
                continue
            if norm in existing_books:
                book = existing_books[norm]
                if not book.image or (hasattr(book.image, 'name') and not book.image.name):
                    filename = f'book_{book.id}_{slugify(book.name)}.png'
                    image_file = create_placeholder_image(book.name, category)
                    book.image.save(filename, image_file, save=False)
                    book.save(update_fields=['image'])
                continue
            title = entry_text[:350]
            author_name = rec.author or 'Unknown Author'
            author, _ = Author.objects.get_or_create(
                name=author_name[:350],
                defaults={'description': 'Auto-created from syllabus'}
            )
            book = Book(
                name=title,
                author=author,
                category=category,
                image=None
            )
            book.save()
            filename = f'book_{book.id}_{slugify(book.name)}.png'
            image_file = create_placeholder_image(book.name, category)
            book.image.save(filename, image_file, save=False)
            book.save(update_fields=['image'])
            existing_books[norm] = book


class Migration(migrations.Migration):
    dependencies = [
        ('library', '0009_book_images'),
    ]

    operations = [
        migrations.RunPython(sync_recommendations_to_books),
    ]
