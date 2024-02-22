FROM python:3.12.2-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

RUN chmod +x /app/run.sh

ENTRYPOINT ["/app/run.sh"]