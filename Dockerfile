FROM python:3-onbuild

EXPOSE 8000

WORKDIR .
COPY . .

RUN pip3 install python-a2s
RUN pip install -r requirements.txt

CMD python manage.py runserver 0.0.0.0:8000 && python manage.py makemigrations && python manage.py migrate
