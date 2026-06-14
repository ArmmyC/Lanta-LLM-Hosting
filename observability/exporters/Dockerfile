FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY platform_exporter.py .

EXPOSE 9108
CMD ["python", "platform_exporter.py"]
