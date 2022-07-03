FROM python

WORKDIR /app

ADD requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD python get_data.py