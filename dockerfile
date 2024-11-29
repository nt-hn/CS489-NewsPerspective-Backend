FROM python:3.9.18-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader vader_lexicon punkt
RUN python -m spacy download en_core_web_sm

COPY . .

ENV PORT=8000 \
   HOST=0.0.0.0 \
   PYTHONUNBUFFERED=1 \
   RAILWAY_ENVIRONMENT=production

CMD gunicorn --bind 0.0.0.0:$PORT wsgi:app