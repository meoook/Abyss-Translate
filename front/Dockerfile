# pull official base image
FROM node:alpine

# set work directory
WORKDIR /usr/src/front

# install dependencies
COPY ./package.json .
COPY ./package-lock.json .
RUN npm update && npm install

# copy project
COPY . .

# react default port
EXPOSE 3000

# CMD ["npm", "start"]
