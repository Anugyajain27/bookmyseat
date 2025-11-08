BookMySeat – Online Movie Ticket Booking System

Overview :-

BookMySeat is a Django-based web application that allows users to browse movies, view theaters, select seats, and book tickets online. The project also includes a secure payment gateway using Razorpay, along with an admin dashboard to monitor revenue, popular movies, and theater statistics.

Features :-

(User Features)
1. User registration and login (with Django Authentication)
2. Browse movies and view details
3. View available theaters for a movie
4. Interactive seat selection
5. Online payment integration with Razorpay
6. Booking confirmation and ticket display

(Admin Features)
1. Manage movies, theaters, and seats
2. View total revenue and popular movies
3. Monitor busiest theaters
4. Access via Django Admin Interface

Tech Stack :-

Component	Technology Used,
Frontend	HTML, CSS, Bootstrap
Backend	Django (Python)
Database	SQLite3
Payment Gateway	Razorpay
Deployment	PythonAnywhere

Installation & Setup :-

1. Clone the repository

git clone https://github.com/Anugyajain27/bookmyseat.git

cd bookmyseat


2. Create a virtual environment

python -m venv venv

source venv/bin/activate      # For Linux/Mac

venv\Scripts\activate         # For Windows



3. Install dependencies

pip install -r requirements.txt



4. Run migrations

python manage.py makemigrations

python manage.py migrate



5. Create a superuser

python manage.py createsuperuser



6. Run the development server

python manage.py runserver



7. Visit the app at http://127.0.0.1:8000/



Admin Access :-

To access the admin dashboard, go to:

http://127.0.0.1:8000/admin/


Use the following credentials (for demo):

Username: anugya

Password: anu@2710



Payment Integration :-

Integrated with Razorpay for secure and real-time payment processing.

Admin Dashboard :-

Displays total revenue, most popular movies, and busiest theaters.

Helps in analyzing booking trends and management.

Deployment :-

The project is deployed on PythonAnywhere for live demonstration.

Live Link: https://anugya27.pythonanywhere.com/

Author:-

Anugya Jain

📧 anugya.jain27@gmail.com

💼 https://www.linkedin.com/in/anugya-jain-21744b290/

🌐 https://github.com/Anugyajain27
