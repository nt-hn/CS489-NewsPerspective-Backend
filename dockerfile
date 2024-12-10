FROM python:3.11.10-slim

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m nltk.downloader vader_lexicon stopwords punkt_tab
RUN python -m spacy download en_core_web_sm

COPY . .

ENV PORT=8000 \
   HOST=0.0.0.0 \
   PYTHONUNBUFFERED=1 \
   RAILWAY_ENVIRONMENT=production

CMD gunicorn --bind 0.0.0.0:$PORT wsgi:app
