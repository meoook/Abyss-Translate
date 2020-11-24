# pull official base image  (upgrade when fix sass problem)
FROM node:14.15.1-alpine3.10

# set work directory
WORKDIR /usr/src/front

# install dependencies
COPY ./package.json .
COPY ./package-lock.json .

RUN npm install

# copy project
COPY . .

# react default port
EXPOSE 3000

# CMD ["npm", "start"]
