# MoodPet (Django + SQLite)
Run locally:
1. python -m venv venv && source venv/bin/activate (linux/mac)
   python -m venv venv && venv\Scripts\Activate.ps1
2. pip install -r requirements.txt
3. python manage.py migrate
4. python manage.py createsuperuser
5. python manage.py runserver
Open http://127.0.0.1:8000/
