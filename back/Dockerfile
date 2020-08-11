FROM python:3.8-slim
WORKDIR /back

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# update packages
RUN apt-get update && \
	apt-get install -y --no-install-recommends build-essenti psycopg2-binary

RUN pip install --upgrade pip

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# ENTRYPOINT [ "sh", "/entrypoint.sh" ]
