from django.shortcuts import render,redirect
from .models import Book,Author,Issue,Fine
from student.models import Student
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils import timezone
import datetime
from .utilities import calcFine,getmybooks
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import auth
from django.conf import settings
from django.http import JsonResponse
import requests
import re
from .models import BookRecommendation


# Book
@login_required(login_url='/aeclibrary/student/signup/')
def allbooks(request):
    requestedbooks,issuedbooks=getmybooks(request.user)
    allbooks=Book.objects.all()
    recommendations=BookRecommendation.objects.all().order_by('id')
    
    return render(request,'library/home.html',{'books':allbooks,'issuedbooks':issuedbooks,'requestedbooks':requestedbooks,'recommendations':recommendations})


def sort(request):
    sort_type=request.GET.get('sort_type')
    sort_by=request.GET.get('sort')
    requestedbooks,issuedbooks=getmybooks(request.user)
    if 'author' in sort_type:
        author_results=Author.objects.filter(name__startswith=sort_by)
        return render(request,'library/home.html',{'author_results':author_results,'issuedbooks':issuedbooks,'requestedbooks':requestedbooks,'selected':'author'})
    else:
        books_results=Book.objects.filter(name__startswith=sort_by)
        return render(request,'library/home.html',{'books_results':books_results,'issuedbooks':issuedbooks,'requestedbooks':requestedbooks,'selected':'book'})


def search(request):
    search_query=request.GET.get('search-query')
    search_by_author=request.GET.get('author')
    requestedbooks,issuedbooks=getmybooks(request.user)

    if search_by_author is not None:
        author_results=Author.objects.filter(name__icontains=search_query)
        return render(request,'library/home.html',{'author_results':author_results,'issuedbooks':issuedbooks,'requestedbooks':requestedbooks})
    else:
        books_results=Book.objects.filter(Q(name__icontains=search_query) | Q(category__icontains=search_query))
        return render(request,'library/home.html',{'books_results':books_results,'issuedbooks':issuedbooks,'requestedbooks':requestedbooks})



@login_required(login_url='/aeclibrary/student/signup/')
@user_passes_test(lambda u: u.is_superuser,login_url='/aeclibrary/student/signup/')
def addbook(request):
    authors=Author.objects.all()
    if request.method=="POST":
        name=request.POST['name']
        category=request.POST['category']
        author=Author.objects.get(id=request.POST['author'])
        image=request.FILES['book-image']
        if author is not None or author != '':
            newbook,created=Book.objects.get_or_create(name=name,image=image,category=category,author=author)
            messages.success(request,'Book - {} Added succesfully '.format(newbook.name))
            return render(request,'library/addbook.html',{'authors':authors,})
        else:
            messages.error(request,'Author not found !')
            return render(request,'library/addbook.html',{'authors':authors,})
    else:
        return render(request,'library/addbook.html',{'authors':authors})



@login_required(login_url='/aeclibrary/student/signup/')
@user_passes_test(lambda u: u.is_superuser,login_url='/aeclibrary/student/signup/')
def deletebook(request,bookID):
    book=Book.objects.get(id=bookID)
    messages.success(request,'Book - {} Deleted succesfully '.format(book.name))
    book.delete()
    return redirect('/aeclibrary/')



#  ISSUES

@login_required(login_url='/aeclibrary/student/signup/')
@user_passes_test(lambda u: not u.is_superuser,login_url='/aeclibrary/student/signup/')
def issuerequest(request,bookID):
    student=Student.objects.filter(student_id=request.user)
    if student:
        book=Book.objects.get(id=bookID)
        issue,created=Issue.objects.get_or_create(book=book,student=student[0])
        messages.success(request,'Book - {} Requested succesfully '.format(book.name))
        return redirect('library_home')
    
    messages.error(request,'You are Not a Student !')
    return redirect('/aeclibrary/')

@login_required(login_url='/aeclibrary/student/signup/')
@user_passes_test(lambda u: not u.is_superuser ,login_url='/aeclibrary/student/signup/')
def myissues(request):
    if Student.objects.filter(student_id=request.user):
        student=Student.objects.filter(student_id=request.user)[0]
        
        if request.GET.get('issued') is not None:
            issues=Issue.objects.filter(student=student,issued=True)
        elif request.GET.get('notissued') is not None:
            issues=Issue.objects.filter(student=student,issued=False)
        else:
            issues=Issue.objects.filter(student=student)

        return render(request,'library/myissues.html',{'issues':issues})
    
    messages.error(request,'You are Not a Student !')
    return redirect('/aeclibrary/')


@login_required(login_url='/admin/')
@user_passes_test(lambda u:  u.is_superuser ,login_url='/admin/')
def requestedissues(request):
    if request.GET.get('studentID') is not None and request.GET.get('studentID') != '':
        try:
            user= User.objects.get(username=request.GET.get('studentID'))
            student=Student.objects.filter(student_id=user)
            if student:
                student=student[0]
                issues=Issue.objects.filter(student=student,issued=False)
                return render(request,'library/allissues.html',{'issues':issues})
            messages.error(request,'No Student found')
            return redirect('/aeclibrary/all-issues/') 
        except User.DoesNotExist:
            messages.error(request,'No Student found')
            return redirect('/aeclibrary/all-issues/')

    else:
        issues=Issue.objects.filter(issued=False)
        return render(request,'library/allissues.html',{'issues':issues})



@login_required(login_url='/admin/')
@user_passes_test(lambda u:  u.is_superuser ,login_url='/aeclibrary/student/signup/')
def issue_book(request,issueID):
    issue=Issue.objects.get(id=issueID)
    issue.return_date=timezone.now() + datetime.timedelta(days=15)
    issue.issued_at=timezone.now()
    issue.issued=True
    issue.save()
    return redirect('/aeclibrary/all-issues/')


@login_required(login_url='/aeclibrary/student/signup/')
@user_passes_test(lambda u:  u.is_superuser ,login_url='/admin/')
def return_book(request,issueID):
    issue=Issue.objects.get(id=issueID)
    calcFine(issue)
    issue.returned=True
    issue.save()
    return redirect('/aeclibrary/all-issues/')


#  FINES

@login_required(login_url='/aeclibrary/student/signup/')
@user_passes_test(lambda u: not u.is_superuser ,login_url='/aeclibrary/student/signup/')
def myfines(request):
    if Student.objects.filter(student_id=request.user):
        student=Student.objects.filter(student_id=request.user)[0]
        issues=Issue.objects.filter(student=student)
        for issue in issues:
            calcFine(issue)
        fines=Fine.objects.filter(student=student)
        return render(request,'library/myfines.html',{'fines':fines})
    messages.error(request,'You are Not a Student !')
    return redirect('/aeclibrary/')


@login_required(login_url='/aeclibrary/student/signup/')
@user_passes_test(lambda u:  u.is_superuser ,login_url='/admin/')
def allfines(request):
    issues=Issue.objects.all()
    for issue in issues:
        calcFine(issue)
    return redirect('/admin/library/fine/')

@login_required(login_url='/aeclibrary/student/signup/')
@user_passes_test(lambda u:  u.is_superuser ,login_url='/admin/')
def deletefine(request,fineID):
    fine=Fine.objects.get(id=fineID)
    fine.delete()
    return redirect('/aeclibrary/all-fines/')

def get_razorpay_client():
    import razorpay
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required(login_url='/aeclibrary/student/signup/')
@user_passes_test(lambda u: not u.is_superuser ,login_url='/aeclibrary/student/signup/')
def payfine(request,fineID):
    fine=Fine.objects.get(id=fineID)
    order_amount = int(fine.amount)*100
    order_currency = 'INR'
    order_receipt = fine.order_id
    
    
    razorpay_order = get_razorpay_client().order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt, ))
    print(razorpay_order)
    
    
    return render(request,'library/payfine.html',
    {'amount':order_amount,'razor_id':settings.RAZORPAY_KEY_ID,
    'reciept':razorpay_order['id'],
    'amount_displayed':order_amount / 100,
    'address':'a custom address',
    'fine':fine, 
    })


@login_required(login_url='/aeclibrary/student/signup/')
@user_passes_test(lambda u: not u.is_superuser ,login_url='/aeclibrary/student/signup/')
def pay_status(request,fineID):
    if request.method == 'POST':
        params_dict={
            'razorpay_payment_id':request.POST['razorpay_payment_id'],
            'razorpay_order_id':request.POST['razorpay_order_id'],
            'razorpay_signature':request.POST['razorpay_signature'],
        }
        try:
            status=get_razorpay_client().utility.verify_payment_signature(params_dict)
            if status is None:
                fine=Fine.objects.get(id=fineID)
                fine.paid=True
                fine.datetime_of_payment=timezone.now()
                fine.razorpay_payment_id=request.POST['razorpay_payment_id']
                fine.razorpay_signature=request.POST['razorpay_signature']
                fine.razorpay_order_id = request.POST['razorpay_order_id']
                fine.save()
                
            messages.success(request,'Payment Succesfull')
        except:
            messages.error(request,'Payment Failure')
    return redirect('/aeclibrary/my-fines/')


# ==============================
# BOOKS RECOMMENDATION FORMAT
# ==============================

RECOMMENDATION_FIELDS = [
    'title', 'author', 'book_type', 'isbn', 'publisher',
    'edition_year', 'book_format', 'copies_recommended', 'existing', 'cost',
]


def _ocr_book_image(image_bytes):
    """Best-effort text extraction from an uploaded textbook image.

    Activates only when OCR_API_URL and OCR_API_KEY are configured in the
    environment. Returns raw extracted text (str) or None when unavailable.
    """
    api_url = getattr(settings, 'OCR_API_URL', '')
    api_key = getattr(settings, 'OCR_API_KEY', '')
    if not (api_url and api_key):
        return None
    try:
        resp = requests.post(
            api_url,
            headers={'Authorization': f'Bearer {api_key}'},
            files={'file': ('book.jpg', image_bytes, 'image/jpeg')},
            timeout=30,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if isinstance(data, dict):
            return data.get('text') or data.get('extracted_text') or ''
        return str(data)
    except Exception:
        return None


def _parse_book_fields(text):
    """Naive heuristic parsing of OCR text into recommendation fields."""
    fields = {k: '' for k in RECOMMENDATION_FIELDS}
    if not text:
        return fields
    isbn_match = re.search(r'(?:ISBN[^\d]{0,5})?(\d[\d\-\s]{8,}\d)', text, re.IGNORECASE)
    if isbn_match:
        fields['isbn'] = isbn_match.group(1).replace(' ', '').replace('-', '')
    if re.search(r'\be-?book\b', text, re.IGNORECASE):
        fields['book_format'] = 'E-book'
    elif re.search(r'\bhard\s?copy\b|\bhardcover\b', text, re.IGNORECASE):
        fields['book_format'] = 'Hard'
    if re.search(r'reference', text, re.IGNORECASE):
        fields['book_type'] = 'Reference Book'
    elif re.search(r'text\s?book', text, re.IGNORECASE):
        fields['book_type'] = 'Textbook'
    year_match = re.search(r'\b(19|20)\d{2}\b', text)
    if year_match:
        fields['edition_year'] = year_match.group(0)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if lines:
        fields['title'] = lines[0][:350]
        for ln in lines[1:]:
            if ln and ln != fields['title']:
                fields['author'] = ln[:350]
                break
    return fields


@login_required(login_url='/aeclibrary/student/signup/')
def add_recommendation(request):
    if request.method == 'POST':
        rec = BookRecommendation()
        if request.FILES.get('image'):
            rec.image = request.FILES['image']
        for field in RECOMMENDATION_FIELDS:
            value = request.POST.get(field, '').strip()
            if field in ('book_type', 'book_format'):
                if value in dict(BookRecommendation._meta.get_field(field).choices):
                    setattr(rec, field, value)
            else:
                setattr(rec, field, value[:350])
        rec.save()
        messages.success(request, 'Book recommendation added.')
        return redirect('library_home')
    return redirect('library_home')


@login_required(login_url='/aeclibrary/student/signup/')
def scan_book(request):
    if request.method != 'POST' or not request.FILES.get('image'):
        return JsonResponse({'ok': False, 'error': 'No image uploaded.'}, status=400)
    image_bytes = request.FILES['image'].read()
    text = _ocr_book_image(image_bytes)
    if text is None:
        return JsonResponse(
            {'ok': False, 'configured': False,
             'message': 'Auto-extract not configured. Please enter details manually.'},
            status=200,
        )
    return JsonResponse({'ok': True, 'configured': True, 'fields': _parse_book_fields(text)})
