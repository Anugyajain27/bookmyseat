from django.db import models
from django.contrib.auth.models import User 
from urllib.parse import urlparse, parse_qs
from datetime import timedelta
from django.utils import timezone


class Movie(models.Model):
    GenreChoices = [
        ('Action', 'Action'),
        ('Drama', 'Drama'),
        ('Comedy', 'Comedy'),
        ('Romance', 'Romance'),
        ('Horror', 'Horror'),
        ('Thriller', 'Thriller'),
    ]

    LanguageChoices = [
        ('Hindi', 'Hindi'),
        ('English', 'English'),
        ('Tamil', 'Tamil'),
        ('Telugu', 'Telugu'),
        ('Spanish', 'Spanish'),
        ('Marathi', 'Marathi'),
    ]

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="movies/")
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    cast = models.TextField()
    description = models.TextField(blank=True, null=True)
    genre = models.CharField(max_length=30, choices=GenreChoices, default='Comedy')
    language = models.CharField(max_length=30, choices=LanguageChoices, default='Hindi')
    trailer_url = models.URLField(blank=True, null=True)

    def yt_url(self):
        if not self.trailer_url:
            return None
        try:
            u = urlparse(self.trailer_url)
            if u.netloc.endswith("youtu.be"):
                vid = u.path.strip("/")
            elif "youtube.com" in u.netloc and u.path == "/watch":
                vid = parse_qs(u.query).get("v", [None])[0]
            elif "youtube.com" in u.netloc and (u.path.startswith("/shorts/") or u.path.startswith("/embed/")):
                vid = u.path.split("/")[2] if len(u.path.split("/")) > 2 else None
            else:
                vid = None
            return f"https://www.youtube.com/embed/{vid}" if vid else None
        except Exception:
            return None

    def __str__(self):
        return self.name


class Theater(models.Model):
    name = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='theaters')
    time = models.DateTimeField()

    def __str__(self):
        return f'{self.name} - {self.movie.name} at {self.time}'


class Seat(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)
    reserved_until = models.DateTimeField(null=True, blank=True)
    reserved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def is_reserved(self):
        if self.reserved_until and timezone.now() < self.reserved_until:
            return True
        return False

    def release_if_expired(self):
        if self.reserved_until and timezone.now() > self.reserved_until:
            self.reserved_until = None
            self.reserved_by = None
            self.save()

    def __str__(self):
        return f'{self.seat_number} in {self.theater.name}'


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Booking by {self.user.username} for {self.seat.seat_number} at {self.theater.name}'
