FROM mcr.microsoft.com/playwright/python:v1.52.0-noble

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app
COPY Scrapping_Agencija /app/nvd-source/Scrapping_Agencija
COPY Scrapping_Jobs /app/nvd-source/Scrapping_Jobs
COPY Scrapping_KarieraMk /app/nvd-source/Scrapping_KarieraMk

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
CMD ["/app/entrypoint.sh"]
