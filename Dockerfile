FROM python:3.9-alpine3.13 
# using python version and alpine the lowest of version images
LABEL maintainer="hameddjf33@gmail.com"
# maintainer of docker image (person or website)
ENV PYTHONUNBUFFERED 1
# say to python = dont want buffer the output / print in console
COPY ./requirements.txt /tmp/requirements.txt
# copy & forward requirements to (temp/requirements.txt) 
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
# copy requirements files(app django) in docker image to (/app)
WORKDIR /app
# set working directory as app folder & default directory the commands are running (when we run command on docker image)
EXPOSE 8000
# expose port for app 

ARG DEV=false
# Creates the dev argument, which is set at the time of creating the image = defaul value is false
# this will override in requirements.dev.txt to the true
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = 'true' ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        hameddjf
# run in alpine image include (
#     22= add apk and install postgresql
#     23= set the virtual dependency packege
#     29= remove /tmp directory = to not depend on the image
#     30= remove the temp build deps (in line 24)  
#     31= create new user in docker image with no password and no directory home / in the last is name of user (we dont want use the root user - dont use root user)
# )
ENV PATH="/py/bin:$PATH"
# update the environment variable inside the image and we updating the path environment variable / define all of the directories where executables can be run
USER hameddjf
# change the root user to hameddjf 