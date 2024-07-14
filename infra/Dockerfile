FROM python:3.9-buster
ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV PYTHONUNBUFFERED=1
COPY . /app/
WORKDIR /app/
RUN pip install -U pip && pip install -r requirements.txt
RUN chmod u+x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
