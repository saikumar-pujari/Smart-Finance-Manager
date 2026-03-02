From windows

Working /app
COPY requirements.txt /app
COPY home /app

RUN apt-get-updates && \
    apt-get install -y python python-pip && \
    pip install -r requriments.txt && \
    cd home

ENTRYPOINT ["python"]
CMD ["manage.py","runserver_plus","localhost:8000"]
