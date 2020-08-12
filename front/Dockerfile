# pull official base image
FROM node:alpine

# set work directory
WORKDIR /usr/src/front

# copy project
COPY . .

# install dependencies
RUN npm install

# react default port
EXPOSE 3000

# CMD ["npm", "start"]
