complaint-management-system
Installation
Linux/Mac
Open terminal using Ctrl+T. Run the following command
git clone https://github.com/khalidsaifullaah/complaint-management-system.git

Create and active virtual environment using
virtualenv -p python3 env
cd venv
source bin/activate

Change the directory using
cd ..
cd Complain_Management_System

Now you need to install python packages to run the app
pip3 install -r requirements.txt

Migrations
python manage.py makemigrations python manage.py migrate

Run Django app
python manage.py runserver

Windows
Open terminal using WinKey+R then Type "cmd" and then click "OK" . Run the following command
git clone https://github.com/khalidsaifullaah/complaint-management-system.git
Install and active virtual environment using
pip install virtualenv
virtualenv env
env\Scripts\activate
Change the directory using
cd Complain_Management_System
Now you need to install python packages to run the app
pip3 install -r requirements.txt
Migrations
python manage.py makemigrations
python manage.py migrate --run-syncdb
Run Django app
python manage.py runserver