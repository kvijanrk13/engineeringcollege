import re

from django.db import migrations
from django.core.files.images import ImageFile
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


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


def clean_book_title(text):
    if not text:
        return ''
    text = re.sub(r'^\d+[\.\)]\s*', '', text).strip()
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Stop at common metadata markers
    markers = [
        'CO-PO-PSO Mapping',
        'Course Outcomes:',
        'CO1:',
        'CO 1:',
        'R22 Syllabus',
        'R25 Syllabus',
        'ANURAG ENGINEERING COLLEGE',
        'ANURAG ENGINEE',
        'L T P C',
        'Upon the successful',
        'Upon successful completion',
        'UNIT -I',
        'UNIT I:',
        'UNIT -II',
        'UNIT II:',
    ]
    
    for marker in markers:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx].strip()
    
    # Remove trailing punctuation
    text = re.sub(r'[\s\-\.\,]+$', '', text).strip()
    
    return text


def normalize(text):
    if not text:
        return ''
    t = text.lower().strip()
    t = re.sub(r'[^a-z0-9\s]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def extract_clean_entries(book_type):
    if not book_type:
        return [], []
    
    parts = book_type.split('/')
    text_part = parts[0] if parts else book_type
    ref_part = parts[1] if len(parts) > 1 else ''
    
    textbooks = []
    references = []
    
    text_entries = re.split(r'[\n]+', text_part)
    for entry in text_entries:
        p = entry.strip()
        if not p:
            continue
        clean = clean_book_title(p)
        if clean and len(clean) > 5:
            textbooks.append(clean)
    
    ref_entries = re.split(r'[\n]+', ref_part)
    for entry in ref_entries:
        p = entry.strip()
        if not p:
            continue
        clean = clean_book_title(p)
        if clean and len(clean) > 5:
            references.append(clean)
    
    return textbooks, references


def rebuild_books(apps, schema_editor):
    Book = apps.get_model('library', 'Book')
    BookRecommendation = apps.get_model('library', 'BookRecommendation')
    Author = apps.get_model('library', 'Author')
    
    # Delete all existing books
    Book.objects.all().delete()
    
    all_books = {}  # normalized_title -> {'title': ..., 'category': ...}
    
    for rec in BookRecommendation.objects.all():
        book_type = rec.book_type or ''
        textbooks, references = extract_clean_entries(book_type)
        
        # Process textbooks
        for entry in textbooks:
            norm = normalize(entry)
            if norm and norm not in all_books:
                all_books[norm] = {
                    'title': entry[:350],
                    'category': 'TEXT'
                }
        
        # Process references
        for entry in references:
            norm = normalize(entry)
            if norm and norm not in all_books:
                all_books[norm] = {
                    'title': entry[:350],
                    'category': 'REFERENCE'
                }
    
    print(f'Creating {len(all_books)} unique books...')
    
    # Create books
    for norm, data in all_books.items():
        author_name = 'Unknown Author'
        author, _ = Author.objects.get_or_create(
            name=author_name,
            defaults={'description': 'Auto-created from syllabus'}
        )
        
        book = Book(
            name=data['title'],
            author=author,
            category=data['category'],
            image=None
        )
        book.save()
        
        # Generate placeholder image
        filename = f'book_{book.id}_{slugify(book.name)}.png'
        image_file = create_placeholder_image(book.name, data['category'])
        book.image.save(filename, image_file, save=False)
        book.save(update_fields=['image'])
    
    text_count = Book.objects.filter(category='TEXT').count()
    ref_count = Book.objects.filter(category='REFERENCE').count()
    total_count = Book.objects.count()
    print(f'TEXT: {text_count}, REFERENCE: {ref_count}, TOTAL: {total_count}')


class Migration(migrations.Migration):
    dependencies = [
        ('library', '0010_sync_recommendations'),
    ]

    operations = [
        migrations.RunPython(rebuild_books),
    ]
