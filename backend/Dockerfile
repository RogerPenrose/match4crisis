FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3 python3-pip libpq-dev gettext
WORKDIR /match4crisis-backend
COPY requirements.txt /match4crisis-backend/requirements.txt
RUN python3 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
COPY requirements.prod.txt /match4crisis-backend/requirements.prod.txt
RUN pip3 install -r requirements.prod.txt

EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
