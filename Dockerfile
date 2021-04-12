FROM python:3.8

ENV DATABASE_HOST=localhost
ENV DATABASE_PORT=5432

RUN wget -O /bin/wait-for-it https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x /bin/wait-for-it

COPY requirements.txt /srv/requirements.txt

WORKDIR /srv

RUN pip install -r requirements.txt

COPY . /srv

EXPOSE 80

ENTRYPOINT ["/srv/entrypoint.sh"]

CMD ["runserver"]
