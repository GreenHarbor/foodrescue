FROM --platform=linux/arm64 python:3.11-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src/app.py .
COPY src/amqp_setup.py .
EXPOSE 5000
CMD ["python", "./app.py"]