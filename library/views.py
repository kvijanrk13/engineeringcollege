from django.shortcuts import render,redirect
from .models import Book,Author,Issue,Fine,BookRecommendation,LibraryStat
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
import re
import os
import markdown


# Book
@login_required(login_url='/aeclibrary/student/signup/')
def allbooks(request):
    requestedbooks,issuedbooks=getmybooks(request.user)
    allbooks=Book.objects.all()
    text_books=allbooks.filter(category='TEXT')
    reference_books=allbooks.filter(category='REFERENCE')
    recommendations=BookRecommendation.objects.all().order_by('id').exclude(title__icontains='laboratory')

    total = allbooks.count()
    issued = Issue.objects.filter(return_date__isnull=True).values('book').distinct().count()
    available = max(total - issued, 0)

    copies_sum = 0
    for rec in recommendations:
        try:
            copies_sum += int((rec.copies_recommended or '0').strip())
        except ValueError:
            pass

    stat, _ = LibraryStat.objects.get_or_create(id=1)
    borrowed = min(stat.borrowed_books, max(copies_sum, 0))
    stat.borrowed_books = borrowed
    stat.save()

    issued = borrowed
    available = max(copies_sum - borrowed, 0)
    total = available + issued

    return render(request,'library/home.html',{'books':allbooks,'text_books':text_books,'reference_books':reference_books,'issuedbooks':issuedbooks,'requestedbooks':requestedbooks,'recommendations':recommendations,'total':total,'issued':issued,'available':available,'copies_sum':copies_sum})


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
    search_query = request.GET.get('search-query', '').strip()
    requestedbooks, issuedbooks = getmybooks(request.user)

    if not search_query:
        messages.warning(request, 'Please enter a search term.')
        return redirect('library_home')

    author_results = Author.objects.filter(name__icontains=search_query)
    books_results = Book.objects.filter(Q(name__icontains=search_query) | Q(category__icontains=search_query))

    return render(request, 'library/search_results.html', {
        'search_query': search_query,
        'author_results': author_results,
        'books_results': books_results,
        'issuedbooks': issuedbooks,
        'requestedbooks': requestedbooks,
    })



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
def borrow_books(request):
    if request.method == "POST":
        selected = request.POST.getlist('sel')
        n = len(selected)
        if n > 0:
            stat, _ = LibraryStat.objects.get_or_create(id=1)
            copies_sum = sum(int((r.copies_recommended or '0').strip() or 0) for r in BookRecommendation.objects.all())
            stat.borrowed_books = min(stat.borrowed_books + n, max(copies_sum, 0))
            stat.save()
            messages.success(request, '{} book(s) borrowed successfully.'.format(n))
        else:
            messages.error(request, 'Select at least one book to borrow.')
    return redirect('library_home')


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
    stat, _ = LibraryStat.objects.get_or_create(id=1)
    if request.GET.get('studentID') is not None and request.GET.get('studentID') != '':
        try:
            user= User.objects.get(username=request.GET.get('studentID'))
            student=Student.objects.filter(student_id=user)
            if student:
                student=student[0]
                issues=Issue.objects.filter(student=student,issued=False)
                return render(request,'library/allissues.html',{'issues':issues,'library_stat':stat})
            messages.error(request,'No Student found')
            return redirect('/aeclibrary/all-issues/') 
        except User.DoesNotExist:
            messages.error(request,'No Student found')
            return redirect('/aeclibrary/all-issues/')

    else:
        issues=Issue.objects.filter(issued=False)
        return render(request,'library/allissues.html',{'issues':issues,'library_stat':stat})



@login_required(login_url='/admin/')
@user_passes_test(lambda u:  u.is_superuser ,login_url='/aeclibrary/student/signup/')
def clear_issues(request):
    if request.method == "POST":
        deleted_count, _ = Issue.objects.filter(issued=False).delete()
        LibraryStat.objects.filter(id=1).update(borrowed_books=Issue.objects.filter(issued=True, returned=False).count())
        messages.success(request, f'{deleted_count} pending issue(s) cleared successfully.')
    return redirect('/aeclibrary/all-issues/')


@login_required(login_url='/admin/')
@user_passes_test(lambda u:  u.is_superuser ,login_url='/aeclibrary/student/signup/')
def issue_book(request,issueID):
    issue=Issue.objects.get(id=issueID)
    if issue.issued:
        messages.error(request, 'Book is already issued.')
        return redirect('/aeclibrary/all-issues/')
    issue.return_date=timezone.now() + datetime.timedelta(days=15)
    issue.issued_at=timezone.now()
    issue.issued=True
    issue.save()
    messages.success(request, 'Book issued successfully.')
    return redirect('/aeclibrary/all-issues/')


@login_required(login_url='/aeclibrary/student/signup/')
@user_passes_test(lambda u:  u.is_superuser ,login_url='/admin/')
def return_book(request,issueID):
    issue=Issue.objects.get(id=issueID)
    calcFine(issue)
    issue.returned=True
    issue.save()
    messages.success(request, 'Book returned successfully.')
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
    fines=Fine.objects.all().order_by('-id')
    return render(request,'library/allfines.html',{'fines':fines})

@login_required(login_url='/aeclibrary/student/signup/')
@user_passes_test(lambda u:  u.is_superuser ,login_url='/admin/')
def deletefine(request,fineID):
    fine=Fine.objects.get(id=fineID)
    fine.delete()
    messages.success(request, 'Fine deleted successfully.')
    return redirect('/aeclibrary/all-fines/')

@login_required(login_url='/aeclibrary/student/signup/')
@user_passes_test(lambda u:  u.is_superuser ,login_url='/admin/')
def update_fine(request,fineID):
    fine=Fine.objects.get(id=fineID)
    if request.method == "POST":
        amount = request.POST.get('amount')
        if amount is not None:
            try:
                fine.amount = float(amount)
                fine.save()
                messages.success(request, 'Fine amount updated successfully.')
            except ValueError:
                messages.error(request, 'Invalid amount.')
        return redirect('/aeclibrary/all-fines/')
    return redirect('/aeclibrary/all-fines/')

@login_required(login_url='/aeclibrary/student/signup/')
@user_passes_test(lambda u:  u.is_superuser ,login_url='/admin/')
def waive_fine(request,fineID):
    fine=Fine.objects.get(id=fineID)
    fine.paid = True
    fine.amount = 0
    fine.save()
    messages.success(request, 'Fine waived successfully.')
    return redirect('/aeclibrary/all-fines/')

@login_required(login_url='/aeclibrary/student/signup/')
def reset_issued(request):
    if request.method == "POST":
        stat, _ = LibraryStat.objects.get_or_create(id=1)
        stat.borrowed_books = 0
        stat.save()
        now = timezone.now()
        Issue.objects.filter(issued=True, returned=False).update(issued=False, returned=True, return_date=now)
        messages.success(request, 'Issued books reset successfully.')
    return redirect('library_home')


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


def documentation(request):
    base = os.path.join(os.path.dirname(__file__), 'docs')
    week1_path = os.path.join(base, 'week1_problem_statement.md')
    srd_path = os.path.join(base, 'srd_week2.md')
    sdd_path = os.path.join(base, 'sdd_week3.md')
    week4_path = os.path.join(base, 'week4_design_structural_models.md')
    week1_text = ''
    srd_text = ''
    sdd_text = ''
    week4_text = ''
    if os.path.exists(week1_path):
        with open(week1_path, 'r', encoding='utf-8') as f:
            week1_text = markdown.markdown(f.read(), extensions=['tables'])
    if os.path.exists(srd_path):
        with open(srd_path, 'r', encoding='utf-8') as f:
            srd_text = markdown.markdown(f.read(), extensions=['tables'])
    if os.path.exists(sdd_path):
        with open(sdd_path, 'r', encoding='utf-8') as f:
            sdd_text = markdown.markdown(f.read(), extensions=['tables'])
    if os.path.exists(week4_path):
        with open(week4_path, 'r', encoding='utf-8') as f:
            week4_text = markdown.markdown(f.read(), extensions=['tables'])
    return render(request, 'library/documentation.html', {
        'week1_text': week1_text,
        'srd_text': srd_text,
        'sdd_text': sdd_text,
        'week4_text': week4_text,
    })

