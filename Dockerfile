FROM python:3.8

WORKDIR /app/

COPY ./app /app
COPY ./requirements.txt /requirements.txt
# para que tome las variables de entorno:
COPY ./.env /.env 

RUN pip install --no-cache-dir -r /requirements.txt

#EXPOSE 8000

CMD ["uvicorn", "main:app", "--host=0.0.0.0","--port=80", "--reload"]