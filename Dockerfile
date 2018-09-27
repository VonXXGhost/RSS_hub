FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends

RUN mkdir /RSS_server
WORKDIR /RSS_server

ADD ./requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ADD . /RSS_server
RUN chmod +x run_*

EXPOSE 8000

ENV PYTHONPATH="/RSS_server/:$PYTHONPATH"