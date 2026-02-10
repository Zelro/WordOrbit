Username: admin 
email: denzelkoro@gmail.com
Pass: 123456





WordOrbit

WordOrbit is a Django-based web application designed to deliver an interactive and user-friendly word-focused experience. The project demonstrates full-stack web development using Django, including backend logic, templates, static asset management, and live deployment.

Live Demo

🔗 Live Site: WordOrbit

WordOrbit is a Django-based web application designed to deliver an interactive and user-friendly word-focused experience. The project demonstrates full-stack web development using Django, including backend logic, templates, static asset management, and live deployment.

Live Demo

🔗 Live Site: https://wordorbit.onrender.com/

Features

Interactive word-based functionality

Clean and responsive user interface

Django-powered backend architecture

Static asset handling (CSS, JavaScript, images)

Admin dashboard for content management

Live deployment for public access

Tech Stack

Backend: Django (Python)

Frontend: HTML, CSS, JavaScript

Database: SQLite (default)

Deployment: Render

Project Structure

WordOrbit/
├── manage.py
├── WordOrbit/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── app/
├── templates/
├── static/
├── requirements.txt
└── build.sh


Installation (Local Setup)

Clone the repository

git clone https://github.com/your-username/WordOrbit.git
cd WordOrbit


Create a virtual environment

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies

pip install -r requirements.txt


Run migrations

python manage.py migrate


Start the development server

python manage.py runserver


Open your browser and visit:

http://127.0.0.1:8000


Deployment

This project is configured for deployment on Render using Gunicorn and a custom build script. Static files are collected automatically during deployment.

Author

Denzel Okoro

License

This project is for educational, professional and personal purposes.