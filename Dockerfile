FROM python:3.9

COPY . /bot 

WORKDIR /bot 

RUN mkdir /bot/images/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["python", "./src/main.py"]
