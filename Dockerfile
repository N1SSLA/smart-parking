FROM python3.12-slim

WORKDIR app

COPY serverrequirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY serverapp .app

EXPOSE 8000

CMD [uvicorn, app.mainapp, --host, 0.0.0.0, --port, 8000]