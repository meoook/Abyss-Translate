# Install the base requirements for the app.
# This stage is to support development.
FROM python:alpine AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Run tests to validate app
FROM node:12-alpine AS app-base
WORKDIR /app
COPY app/package.json app/yarn.lock ./
# RUN yarn config set registry https://registry.npm.taobao.org
# RUN yarn install
# RUN npm config set registry https://registry.npm.taobao.org/
RUN npm install -g cnpm --registry=https://registry.npm.taobao.org
RUN cnpm install
COPY app/spec ./spec
COPY app/src ./src
RUN cnpm test

# Clear out the node_modules and create the zip
FROM app-base AS app-zip-creator
RUN rm -rf node_modules && \
    apk add zip && \
    zip -r /app.zip /app

# Dev-ready container - actual files will be mounted in
FROM base AS dev
CMD ["mkdocs", "serve", "-a", "0.0.0.0:8000"]

# Do the actual build of the mkdocs site
FROM base AS build
COPY . .
RUN mkdocs build

# Extract the static content from the build
# and use a nginx image to serve the content
FROM nginx:alpine
COPY --from=app-zip-creator /app.zip /usr/share/nginx/html/assets/app.zip
COPY --from=build /app/site /usr/share/nginx/html
