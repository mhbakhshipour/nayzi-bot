FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /nayzi_bot
WORKDIR /nayzi_bot
COPY requirements.txt /nayzi_bot/
RUN pip install -r requirements.txt
COPY . /nayzi_bot/