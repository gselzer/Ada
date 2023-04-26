FROM ubuntu:22.04
RUN apt-get -y update
RUN apt-get -y install python3 python3-pip
# RUN apt-get -y install python3-opencv # no need to get beefy!
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
CMD ["flask", "--app", "ada", "run", "--host", "0.0.0.0"]