# pull official base image
FROM node:alpine

# set work directory
WORKDIR /usr/src/front

# install dependencies
COPY . .
RUN npm install

# copy project
COPY ./package.json .

# react default port
EXPOSE 3000

# CMD ["npm", "start"]
