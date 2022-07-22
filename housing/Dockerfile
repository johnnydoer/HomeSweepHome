FROM python

WORKDIR /app

ADD requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x headers.sh

RUN bash ./headers.sh

CMD python get_data.py