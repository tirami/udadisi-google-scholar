FROM ubuntu:14.04

RUN mkdir /udadisi-web
ADD . /udadisi-web
RUN chmod -R 755 /udadisi-web
WORKDIR /udadisi-web

RUN apt-get update
RUN apt-get install -y python python-dev python-pip
RUN pip install -r requirements.txt
RUN python -m nltk.downloader stopwords
EXPOSE 5000
CMD python application.py