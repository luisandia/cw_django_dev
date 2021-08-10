FROM python:3.7
LABEL Luis Andia

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
RUN useradd -ms /bin/bash dockeruser
# RUN usermod -aG dockeruser root

COPY . /app
RUN chown -R dockeruser:dockeruser /app

CMD sh ./entrypoint.sh