from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Theater, Seat, Booking
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone
import razorpay
from django.db.models import Sum, Count
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User

@staff_member_required
def admin_dashboard(request):
    # Temporarily skip revenue calculation
    total_revenue = 0  # You can update this later if you add ticket pricing

    # Most popular movies
    popular_movies = (
        Movie.objects
        .annotate(total_bookings=Count('booking'))
        .order_by('-total_bookings')[:5]
    )

    # Busiest theaters
    busiest_theaters = (
        Theater.objects
        .annotate(total_bookings=Count('booking'))
        .order_by('-total_bookings')[:5]
    )

    from django.contrib.auth.models import User
    total_users = User.objects.count()
    total_bookings = Booking.objects.count()

    context = {
        'total_revenue': total_revenue,
        'popular_movies': popular_movies,
        'busiest_theaters': busiest_theaters,
        'total_users': total_users,
        'total_bookings': total_bookings,
    }
    return render(request, 'movies/admin_dashboard.html', context)



# -------------------- Payment Start --------------------
def start_payment(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)  # ✅ add this
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount = 20000
    payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})

    return render(request, "movies/payment.html", {
        'payment': payment,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'theater': theater,          # ✅ pass to template
        'theater_id': theater_id
    })



# -------------------- Movie Listing --------------------
def movie_list(request):
    search_query = request.GET.get('search')
    genre_filter = request.GET.get('genre')
    language_filter = request.GET.get('language')

    movies = Movie.objects.all()
    if search_query:
        movies = movies.filter(name__icontains=search_query)
    if genre_filter:
        movies = movies.filter(genre__iexact=genre_filter)
    if language_filter:
        movies = movies.filter(language__iexact=language_filter)

    return render(request, 'movies/movie_list.html', {
        'movies': movies,
        'selected_genre': genre_filter,
        'selected_language': language_filter
    })


def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)
    return render(request, 'movies/theater_list.html', {'movie': movie, 'theaters': theaters})


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, "movies/movie_detail.html", {"movie": movie})


# -------------------- Seat Booking (with timeout) --------------------
@login_required(login_url='/login/')
def book_seats(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(theater=theater)

    # 🔁 Release expired reservations before showing seats
    for seat in seats:
        seat.release_if_expired()

    if request.method == 'POST':
        selected_seats = request.POST.getlist('seats')

        if not selected_seats:
            return render(request, "movies/seat_selection.html", {
                'theater': theater,
                "seats": seats,
                'error': "No seat selected"
            })

        error_seats = []
        reserved_seats = []

        for seat_id in selected_seats:
            seat = get_object_or_404(Seat, id=seat_id, theater=theater)

            # Skip if already booked or reserved by someone else
            if seat.is_booked or (seat.is_reserved() and seat.reserved_by != request.user):
                error_seats.append(seat.seat_number)
                continue

            # Reserve for 5 minutes
            seat.reserved_until = timezone.now() + timedelta(minutes=5)
            seat.reserved_by = request.user
            seat.save()
            reserved_seats.append(seat.seat_number)

        if error_seats:
            error_message = f"These seats are unavailable: {', '.join(error_seats)}"
            return render(request, 'movies/seat_selection.html', {
                'theater': theater,
                "seats": seats,
                'error': error_message
            })

        # Store temporarily reserved seats in session for payment
        request.session['selected_seats'] = selected_seats
        request.session['theater_id'] = theater.id

        return redirect('start_payment', theater_id=theater.id)

    return render(request, 'movies/seat_selection.html', {'theater': theater, "seats": seats})


# -------------------- Payment Success --------------------
def payment_success(request):
    payment_id = request.GET.get("payment_id")
    theater_id = request.session.get("theater_id")
    selected_seats = request.session.get("selected_seats", [])

    if not theater_id or not selected_seats:
        messages.error(request, "No booking found in session.")
        return redirect("profile")

    theater = get_object_or_404(Theater, id=theater_id)
    booked_seats = []
    error_seats = []

    for seat_id in selected_seats:
        seat = get_object_or_404(Seat, id=seat_id, theater=theater)

        # Ensure reservation still valid
        if seat.is_booked or seat.reserved_by != request.user:
            error_seats.append(seat.seat_number)
            continue

        # Confirm booking
        Booking.objects.create(
            user=request.user,
            seat=seat,
            movie=theater.movie,
            theater=theater
        )
        seat.is_booked = True
        seat.reserved_until = None
        seat.reserved_by = None
        seat.save()
        booked_seats.append(seat.seat_number)

    # Send email + success message as before
    if booked_seats:
        subject = f"🎟️ Ticket Confirmation - {theater.movie.name}"
        message = f"""
        Hello {request.user.username},

        Your booking is confirmed! ✅

        🎬 Movie: {theater.movie.name}
        📍 Theater: {theater.name}
        🪑 Seats: {', '.join(booked_seats)}
        📅 Show Time: {theater.time.strftime('%d %B %Y, %I:%M %p')}

        Thank you for booking with BookMyShow Clone!
        Enjoy your movie 🍿
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email])

    request.session.pop("selected_seats", None)
    request.session.pop("theater_id", None)

    messages.success(request, "Payment successful! Booking confirmed.")
    return redirect("profile")

# -------------------- Payment Failed --------------------
def payment_failed(request):
    messages.error(request, "Payment failed. Please try again.")
    return redirect("profile")

