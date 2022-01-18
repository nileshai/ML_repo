FROM ubuntu:latest
MAINTAINER nilesh@uniphore.com


RUN apt-get update -y && apt-get install -y python3 python3-pip
RUN python3 -m pip install aspect-based-sentiment-analysis
RUN python3 -m pip install flask
RUN python3 -m pip install flask_cors
RUN python3 -m pip install simplejson
RUN python3 -m pip install pandas
RUN python3 -m pip install click==7.0
RUN python3 -m pip install Exit

RUN mkdir -p /home/workdir
WORKDIR /home/workdir


COPY . .




#CMD [ "streamlit", "run", "test_simscore_ui.py" ]

EXPOSE 5001
ENTRYPOINT [ "python3" ]
CMD [ "api.py" ]






