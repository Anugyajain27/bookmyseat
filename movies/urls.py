
from django.urls import path
from . import views

urlpatterns=[
    path('',views.movie_list,name='movie_list'),
    path('<int:movie_id>/theaters',views.theater_list,name='theater_list'),
    path('theater/<int:theater_id>/seats/book/',views.book_seats,name='book_seats'),
    path('<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path("movie/<int:pk>/", views.movie_detail, name="movie_detail"),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("payment/failed/", views.payment_failed, name="payment_failed"),
    path("payment/start/<int:theater_id>/", views.start_payment, name="start_payment"),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard')
]