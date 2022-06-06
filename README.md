
## run local 
#setup
python manage.py add_data
python manage.py makemigrations
python manage.py migrate

#start server
python manage.py runserver
or via Waitress:
waitress-serve --listen=127.0.0.1:8000 MDAapp.wsgi:application
