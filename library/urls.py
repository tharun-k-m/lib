# library/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list_view, name='book-list'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('book/<int:pk>/', views.book_detail_view, name='book-detail'),
    path('profile/', views.profile_view, name='profile'),
    path('book/<int:pk>/borrow/', views.borrow_book, name='borrow-book'),
    path('book/<int:pk>/buy/', views.buy_book, name='buy-book'),
    path('book/<int:pk>/favorite/', views.favorite_book, name='favorite-book'),
    path('return-book/<int:pk>/', views.return_book, name='return-book'),
]
