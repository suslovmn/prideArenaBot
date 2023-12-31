FROM python:3.10
WORKDIR /app
COPY requirements.txt requirements.txt
COPY . .
RUN pip install -U pip
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
