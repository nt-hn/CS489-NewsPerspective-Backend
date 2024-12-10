from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models.article_analyzer import ArticleAnalyzer
from get_content_using_url import get_page_text
from GPT import GPTCompareArticles
import nltk
import os
import ssl

app = Flask(__name__)

if Config.ALLOWED_ORIGINS == ['*']:
    CORS(app)
else:
    CORS(app, origins=Config.ALLOWED_ORIGINS)

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt_tab', quiet=True)
nltk.download('vader_lexicon', quiet=True)
nltk.download('stopwords', quiet=True)

analyzer = ArticleAnalyzer(Config.NEWS_API_KEY)
gpt = GPTCompareArticles(Config.OPENAI_API_KEY)

@app.route('/api/analyze', methods=['POST'])
def analyze_article():
    try:
        data = request.get_json()
        
        if not data or 'article_text' not in data:
            return jsonify({
                'error': 'No article text provided',
                'status': 'error'
            }), 400
            
        article_text = data['article_text']
        
        analysis = analyzer.analyze_article(article_text)
        
        related_articles = analyzer.find_related_articles(analysis['keywords'])
        
        response = {
            'status': 'success',
            'analysis': analysis['bias_analysis'],
            'keywords': analysis['keywords'],  
            'political_analysis': analysis['political_analysis'],
            'related_articles': related_articles,
            'GPT_Compare': ''
        }
        
        if len(related_articles) > 0:
            content = get_page_text(related_articles[0]['url'])
            comparision_result = gpt.compare_articles(article_text, content)
            response['GPT_Compare'] = comparision_result       
             
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'environment': os.getenv('RAILWAY_ENVIRONMENT', 'development')
    })

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'News Analysis API',
        'status': 'running',
        'endpoints': {
            'analyze': '/api/analyze',
            'health': '/api/health'
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)
