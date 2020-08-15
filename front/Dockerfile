# pull official base image
FROM node:alpine

# set work directory
WORKDIR /usr/src/front

# SET IP
ARG BACKEND_API_URL
ENV BACKEND_API_URL $BACKEND_API_URL

# install dependencies
COPY ./package.json .
RUN npm update && npm install

# copy project
COPY . .

# react default port
EXPOSE 3000

# CMD ["npm", "start"]
