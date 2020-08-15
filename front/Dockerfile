# pull official base image
FROM node:alpine

# set work directory
WORKDIR /usr/src/front

# install dependencies
COPY ./package.json .
RUN npm update && npm install

# copy project
COPY . .

# react default port
EXPOSE 3000

# create and set user
RUN adduser -D user \
    && chown -R user:user /usr/src/front/
USER user

# CMD ["npm", "start"]
