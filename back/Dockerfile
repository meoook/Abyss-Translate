# pull official base image
# FROM python:3.8.3-slim
FROM python:3.8-alpine

# set work directory
WORKDIR /usr/src/back

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev

# RUN apt-get update \
#     && apt-get install -y --no-install-recommends \
#         postgresql-client \
#     && rm -rf /var/lib/apt/lists/*

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

# django default port
EXPOSE 8000

# create and set user
RUN adduser -D user \
    && chown -R user:user /usr/src/back/ \
    && chmod -R 755 /usr/src/back/users \
    && chmod +x /usr/src/back/entrypoint.sh
USER user

# run entrypoint.sh
ENTRYPOINT ["sh", "/usr/src/back/entrypoint.sh"]

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]