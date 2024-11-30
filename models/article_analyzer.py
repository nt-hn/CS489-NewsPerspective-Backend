from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import spacy
import numpy as np
from string import punctuation
from newsapi import NewsApiClient
from .bias_analyzer import BiasAnalyzer, PoliticalAnalyzer

class KeywordExtractor:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.stop_words = set(stopwords.words('english'))
        self.stop_words.update(['would', 'could', 'should', 'may', 'might', 'must', 'need'])
        
    def extract_keywords(self, text):
        """Extract keywords using multiple methods and combine results"""
        doc = self.nlp(text)
        
        noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks]
        entities = [ent.text.lower() for ent in doc.ents]
        
        sentences = [sent.text for sent in doc.sents]
        tfidf = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        tfidf_matrix = tfidf.fit_transform(sentences)
        
        feature_names = tfidf.get_feature_names_out()
        tfidf_scores = np.asarray(tfidf_matrix.mean(axis=0)).ravel()
        top_tfidf = [feature_names[i] for i in tfidf_scores.argsort()[-10:][::-1]]
        
        important_words = []
        for token in doc:
            if (not token.is_stop and not token.is_punct and 
                token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and
                len(token.text) > 2):
                important_words.append(token.text.lower())
        
        all_keywords = set(noun_phrases + entities + top_tfidf + important_words)
        
        filtered_keywords = []
        for keyword in all_keywords:
            keyword = keyword.strip()
            if (len(keyword) > 2 and 
                not keyword.isnumeric() and 
                not all(c in punctuation for c in keyword)):
                filtered_keywords.append(keyword)
        
        keyword_scores = {}
        for keyword in filtered_keywords:
            score = 0
            if keyword in noun_phrases: score += 2
            if keyword in entities: score += 2
            if keyword in top_tfidf: score += 3
            if keyword in important_words: score += 1
            keyword_scores[keyword] = score
        
        sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        return [k for k, s in sorted_keywords[:5]]

class ArticleAnalyzer:
    def __init__(self, news_api_key):
        self.newsapi = NewsApiClient(api_key=news_api_key)
        self.bias_analyzer = BiasAnalyzer()
        self.keyword_extractor = KeywordExtractor()
    
    def analyze_article(self, article_text):
        bias_analysis = self.bias_analyzer.analyze(article_text)
        keywords = self.keyword_extractor.extract_keywords(article_text)
        
        political_analyzer = PoliticalAnalyzer()
        political_analysis = political_analyzer.analyze_political_leaning(article_text)
        
        return {
            'bias_analysis': bias_analysis,
            'keywords': keywords,
            'political_analysis': political_analysis
        }
    
    def find_related_articles(self, keywords, max_articles=10):
        query = ' AND '.join(f'"{keyword}"' for keyword in keywords[:3])
        
        try:
            articles = self.newsapi.get_everything(
                q=query,
                language='en',
                sort_by='relevancy',
                page_size=max_articles
            )
            
            filtered_articles = []
            for article in articles.get('articles', []):
                content = (article.get('title', '') + ' ' + 
                         article.get('description', '')).lower()
                keyword_matches = sum(1 for k in keywords if k.lower() in content)
                if keyword_matches >= 2:
                    filtered_articles.append(article)
            
            return filtered_articles[:max_articles]
        except Exception as e:
            print(f"Error fetching related articles: {e}")
            return []
