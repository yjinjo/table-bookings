FROM python:3.11
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY table-bookings/. /app/
EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
