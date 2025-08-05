# library/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from .models import Book, Genre, Lending, Favorite, Purchase, UserProfile, Review
from .forms import UserRegisterForm, SignInForm, ReviewForm


def book_list_view(request):
    """
    A view to display a list of all books, with search and filter functionality.
    """
    query = request.GET.get('q')  # Get the search query from the URL
    genre_id = request.GET.get('genre')  # Get the selected genre from the URL

    books = Book.objects.filter(is_available=True)  # Start with all available books

    # Apply search filter if a query is provided
    if query:
        books = books.filter(
            Q(title__icontains=query) |  # search by title
            Q(author__first_name__icontains=query) |  # search by author first name
            Q(author__last_name__icontains=query)  # search by author last name
        ).distinct()

    # Apply genre filter if a genre is selected
    if genre_id and genre_id != 'all':
        books = books.filter(genre_id=genre_id)

    # Get all genres to populate the filter dropdown
    genres = Genre.objects.all().order_by('name')

    # Context to be passed to the template
    context = {
        'book_list': books,
        'genres': genres,
        'query': query,  # Pass the query back to the template to pre-fill the search box
        'selected_genre': genre_id,  # Pass the selected genre back to the template
    }

    return render(request, 'library/book_list.html', context=context)



def book_detail_view(request, pk):
    """
    A view to display a single book's details, including reviews and a review form.
    """
    book = get_object_or_404(Book, pk=pk)
    reviews = book.reviews.all()
    user_review = None

    if request.user.is_authenticated:
        # Check if the user has already reviewed this book
        try:
            user_review = Review.objects.get(user=request.user, book=book)
            review_form = None # Don't show the form if they have already reviewed
        except Review.DoesNotExist:
            review_form = ReviewForm()

    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.user = request.user
            new_review.book = book
            new_review.save()
            return redirect('book-detail', pk=book.pk) # Redirect to prevent form re-submission

    context = {
        'book': book,
        'reviews': reviews,
        'review_form': review_form,
        'user_review': user_review,
    }
    return render(request, 'library/book_detail.html', context)


@login_required
def profile_view(request):
    """
    A view to display the user's profile and their lists of books.
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Get the books associated with the user
    borrowed_books = Lending.objects.filter(user=request.user, returned=False).select_related('book')
    purchased_books = Purchase.objects.filter(user=request.user).select_related('book')
    favorited_books = Favorite.objects.filter(user=request.user).select_related('book')

    # Check for overdue books
    now = timezone.now()
    overdue_books = [book for book in borrowed_books if book.due_date < now]

    context = {
        'user_profile': user_profile,
        'borrowed_books': borrowed_books,
        'purchased_books': purchased_books,
        'favorited_books': favorited_books,
        'overdue_books': overdue_books,
    }
    return render(request, 'library/profile.html', context)


# The @login_required decorator has been removed from this function.
def signup(request):
    """
    View for user registration.
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after registration
            return redirect('book-list')  # Redirect to the homepage after successful signup
    else:
        form = UserRegisterForm()

    return render(request, 'library/signup.html', {'form': form})


def signin(request):
    """
    View for user login.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('book-list')  # Redirect to homepage on successful login
    else:
        form = AuthenticationForm()
    return render(request, 'library/signin.html', {'form': form})


def signout(request):
    """
    View for user logout.
    """
    logout(request)
    return redirect('book-list')


@login_required
@require_POST
def borrow_book(request, pk):
    """
    Handles an AJAX request to borrow a book.
    """
    book = get_object_or_404(Book, pk=pk)

    # Check if the book is available
    if not book.is_available:
        return JsonResponse({'error': 'This book is not available for borrowing.'}, status=400)

    # Check if the user has already borrowed this book
    if Lending.objects.filter(user=request.user, book=book, returned=False).exists():
        return JsonResponse({'error': 'You have already borrowed this book.'}, status=400)

    try:
        # Create a new lending record
        due_date = timezone.now() + timedelta(days=14)
        Lending.objects.create(user=request.user, book=book, due_date=due_date)

        # Mark the book as unavailable
        book.is_available = False
        book.save()

        return JsonResponse({'message': 'Book borrowed successfully!'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def buy_book(request, pk):
    """
    Handles an AJAX request to buy a book.
    """
    book = get_object_or_404(Book, pk=pk)

    # Check if the book is available or already sold
    if book.is_sold:
        return JsonResponse({'error': 'This book has already been sold.'}, status=400)

    if not book.is_available:
        return JsonResponse({'error': 'This book is not available for purchase.'}, status=400)

    try:
        # Check if user has already bought this book
        if Purchase.objects.filter(user=request.user, book=book).exists():
            return JsonResponse({'error': 'You have already purchased this book.'}, status=400)

        # Create a new purchase record
        Purchase.objects.create(user=request.user, book=book)

        # Mark the book as sold and unavailable
        book.is_available = False
        book.is_sold = True
        book.save()

        return JsonResponse({'message': 'Book purchased successfully!'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def favorite_book(request, pk):
    """
    Handles an AJAX request to favorite a book.
    """
    book = get_object_or_404(Book, pk=pk)

    # Check if the user has already favorited this book
    if Favorite.objects.filter(user=request.user, book=book).exists():
        return JsonResponse({'error': 'You have already favorited this book.'}, status=400)

    try:
        # Create a new favorite record
        Favorite.objects.create(user=request.user, book=book)
        return JsonResponse({'message': 'Book added to favorites!'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def return_book(request, pk):
    """
    Handles an AJAX request to return a borrowed book.
    """
    try:
        # Find the lending record for the user and the book
        lending = Lending.objects.get(user=request.user, book__id=pk, returned=False)

        # Mark the book as returned
        lending.returned = True
        lending.save()

        # Mark the book as available again in the main catalog
        book = lending.book
        book.is_available = True
        book.save()

        return JsonResponse({'message': 'Book returned successfully!'})
    except Lending.DoesNotExist:
        return JsonResponse({'error': 'This book is not currently borrowed by you.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
