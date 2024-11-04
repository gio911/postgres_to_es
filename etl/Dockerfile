FROM python:3.10

WORKDIR /opt/etl

COPY requirements.txt requirements.txt


# mkdir -p создает директории только в том случае, если они еще не существуют,
# веб-серверы (например, Nginx или Apache) ожидают, что статические файлы будут размещены в определенных директориях.
RUN pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x main.py
ENTRYPOINT ["python", "main.py"]

