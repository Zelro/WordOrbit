# WordOrbit

**WordOrbit** is a full‑stack Django web application built as a portfolio project to demonstrate backend engineering, full‑stack development, and production‑ready GitHub practices. The project highlights clean architecture, scalable backend design, and real‑world deployment workflows.

---

## Live Demo

🔗 **Live Site:** [https://wordorbit.onrender.com/](https://wordorbit.onrender.com/)

---
  
## Screenshots

### Landing Page

![WordOrbit Landing Page](screenshots/landing_page.png)

### Gameplay Interface

![WordOrbit Gameplay](screenshots/gameplay.png)

---

## Project Summary

WordOrbit showcases practical experience in building and deploying a full‑stack web application using Django. It emphasizes backend logic, application structure, environment configuration, and maintainable code organization. The project is designed to reflect industry‑standard development practices that are relevant to backend and full‑stack engineering roles.

Key focus areas include:

* Backend architecture and Django application design
* Full‑stack integration between server logic and UI
* Environment management and production configuration
* Version control and GitHub portfolio presentation

---

## Key Features

* Modular Django backend with organized app structure
* Dynamic template rendering and routing
* Responsive front‑end interface
* Secure environment variable configuration (.env)
* Static and media file management
* Django admin dashboard for data management
* Production deployment with Gunicorn

---

## Technical Highlights (Backend & Full‑Stack)

* Designed scalable Django project architecture
* Implemented environment‑based configuration for security
* Structured reusable templates and static assets
* Managed database migrations and application state
* Configured production deployment pipeline
* Maintained clean Git commit history and repository structure

---

## Tech Stack

* **Backend:** Django (Python)
* **Frontend:** HTML, CSS, JavaScript
* **Database:** SQLite
* **Deployment:** Render + Gunicorn
* **Version Control:** Git & GitHub

---

## Project Structure

```
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
```

The repository is organized to reflect real‑world Django project standards, making it easy for recruiters and collaborators to review the codebase.

---

## Installation (Local Setup)

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/WordOrbit.git
   cd WordOrbit
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the project root and add:

   ```env
   SECRET_KEY=your_secret_key
   DEBUG=True
   ```

5. **Apply database migrations**

   ```bash
   python manage.py migrate
   ```

6. **Run the development server**

   ```bash
   python manage.py runserver
   ```

7. Visit:

   ```
   http://127.0.0.1:8000
   ```

---

## Deployment

The application is configured for deployment on Render using Gunicorn and an automated build script. Static files are collected during deployment to ensure proper production performance and reliability.

---

## Portfolio Value

This project demonstrates:

* Backend engineering with Django
* Full‑stack web development skills
* Production deployment workflows
* Clean GitHub repository organization
* Readable, maintainable code suitable for collaboration

It is intended to serve as a representative portfolio piece for backend and full‑stack developer roles.

---

## Author

**Denzel Okoro**

---

## License

This project is intended for educational and portfolio use.
