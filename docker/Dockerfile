FROM python:latest

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

#Install Cron
RUN apt-get update
RUN apt-get -y install cron

COPY . /camera_snapshots
WORKDIR /camera_snapshots

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PYTHONPATH=$PYTHONPATH:/camera_snapshots/

RUN crontab -l | { cat; echo "* * * * * /opt/venv/bin/python /camera_snapshots/snapshot.py"; } | crontab -

# Run the command on container startup
CMD ["cron", "-f"]
#CMD [ "python", "snapshot.py" ]
