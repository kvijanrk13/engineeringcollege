import os
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


def add_book_images(apps, schema_editor):
    Book = apps.get_model('library', 'Book')
    BookRecommendation = apps.get_model('library', 'BookRecommendation')

    for book in Book.objects.filter(image='').union(Book.objects.filter(image__isnull=True)):
        filename = f'book_{book.id}_{slugify(book.name)}.png'
        image_file = create_placeholder_image(book.name, book.category)
        book.image.save(filename, image_file, save=False)
        book.save(update_fields=['image'])

    for rec in BookRecommendation.objects.filter(image='').union(BookRecommendation.objects.filter(image__isnull=True)):
        filename = f'rec_{rec.id}_{slugify(rec.title)}.png'
        image_file = create_placeholder_image(rec.title or 'Book', '')
        rec.image.save(filename, image_file, save=False)
        rec.save(update_fields=['image'])


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0008_r22_it_syllabus'),
    ]

    operations = [
        migrations.RunPython(add_book_images),
    ]
