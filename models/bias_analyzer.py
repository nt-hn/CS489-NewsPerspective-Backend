import spacy
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
from collections import defaultdict
import numpy as np

class PoliticalAnalyzer:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        
        self.partisan_indicators = {
            'left': {
                'terms': {
                    'progressive', 'liberal', 'democratic socialism', 'social justice',
                    'climate action', 'gun control', 'medicare for all', 'reproductive rights',
                    'systemic racism', 'wealth inequality', 'workers rights'
                },
                'phrases': [
                    'racial equity', 'green new deal', 'universal healthcare',
                    'economic justice', 'income inequality', 'living wage'
                ]
            },
            'right': {
                'terms': {
                    'conservative', 'traditional values', 'free market', 'second amendment',
                    'small government', 'deregulation', 'fiscal responsibility', 
                    'law and order', 'border security', 'religious freedom'
                },
                'phrases': [
                    'family values', 'school choice', 'tax cuts',
                    'individual liberty', 'states rights', 'constitutional rights'
                ]
            }
        }
        
        self.framing_patterns = {
            'immigration': {
                'left': ['undocumented immigrants', 'asylum seekers', 'refugees'],
                'right': ['illegal aliens', 'border crisis', 'illegal immigration']
            },
            'economy': {
                'left': ['wealth gap', 'corporate greed', 'fair share'],
                'right': ['free enterprise', 'job creators', 'market forces']
            },
            'healthcare': {
                'left': ['universal healthcare', 'healthcare rights', 'public option'],
                'right': ['market-based healthcare', 'private insurance', 'personal responsibility']
            }
        }
    
    def analyze_political_leaning(self, text):
        doc = self.nlp(text.lower())
        text_lower = text.lower()
        
        scores = {
            'left': 0,
            'right': 0,
            'indicators': {
                'left': [],
                'right': []
            }
        }
        
        for direction in ['left', 'right']:
            for term in self.partisan_indicators[direction]['terms']:
                if term in text_lower:
                    scores[direction] += 1
                    scores['indicators'][direction].append(term)
            
            for phrase in self.partisan_indicators[direction]['phrases']:
                if phrase in text_lower:
                    scores[direction] += 1.5  
                    scores['indicators'][direction].append(phrase)
        
        for issue, frames in self.framing_patterns.items():
            for direction, patterns in frames.items():
                for pattern in patterns:
                    if pattern in text_lower:
                        scores[direction] += 1
                        scores['indicators'][direction].append(f"{issue}: {pattern}")
        
        total_score = scores['left'] + scores['right']
        if total_score > 0:
            left_percentage = (scores['left'] / total_score) * 100
            right_percentage = (scores['right'] / total_score) * 100
        else:
            left_percentage = right_percentage = 0
        
        if left_percentage > right_percentage:
            if left_percentage > 70:
                leaning = "Strong Left"
            else:
                leaning = "Moderate Left"
        elif right_percentage > left_percentage:
            if right_percentage > 70:
                leaning = "Strong Right"
            else:
                leaning = "Moderate Right"
        else:
            leaning = "Neutral/Centrist"
        
        return {
            'leaning': leaning,
            'left_percentage': round(left_percentage, 2),
            'right_percentage': round(right_percentage, 2),
            'evidence': {
                'left_indicators': list(set(scores['indicators']['left'])),
                'right_indicators': list(set(scores['indicators']['right']))
            }
        }

class BiasAnalyzer:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.sid = SentimentIntensityAnalyzer()
        
        self.opinion_words = {
            'believe', 'think', 'feel', 'suggest', 'seem', 'appear', 'suspect',
            'assume', 'speculate', 'guess', 'imagine', 'presume', 'suppose'
        }
        
        self.extreme_words = {
            'always', 'never', 'everyone', 'nobody', 'definitely', 'absolutely',
            'all', 'none', 'every', 'impossible', 'completely', 'totally'
        }
        
        self.hedge_words = {
            'possibly', 'probably', 'maybe', 'perhaps', 'seemingly',
            'allegedly', 'reportedly', 'might', 'could', 'may'
        }
        
        self.emotional_words = {
            'amazing', 'wonderful', 'terrible', 'horrible', 'beautiful',
            'awesome', 'fantastic', 'dreadful', 'spectacular', 'extraordinary'
        }
        
        self.loaded_words = {
            'controversial', 'radical', 'extremist', 'progressive',
            'conservative', 'liberal', 'notorious', 'infamous'
        }
        
    def _detect_bias_indicators(self, doc):
        indicators = defaultdict(list)
        
        for sent in doc.sents:
            sent_text = sent.text.strip()
            sent_lower = sent_text.lower()
            
            if any(word in sent_lower for word in self.opinion_words):
                indicators['opinion_statements'].append(sent_text)
            
            if any(word in sent_lower for word in self.extreme_words):
                indicators['extreme_language'].append(sent_text)
            
            if any(word in sent_lower for word in self.hedge_words):
                indicators['hedging'].append(sent_text)
            
            if any(word in sent_lower for word in self.emotional_words):
                indicators['emotional_language'].append(sent_text)
            
            if any(word in sent_lower for word in self.loaded_words):
                indicators['loaded_words'].append(sent_text)
            
            if any(word in sent_lower for word in ['studies show', 'research shows', 'experts say']):
                indicators['unsubstantiated_claims'].append(sent_text)
            
            if any(word in sent_lower for word in ['all', 'every', 'none', 'always', 'never']):
                indicators['generalizations'].append(sent_text)
        
        return {k: v for k, v in indicators.items() if v}

    def analyze(self, text):
        doc = self.nlp(text)
        
        analysis = {
            'sentiment_scores': self._analyze_sentiment(text),
            'bias_indicators': self._detect_bias_indicators(doc),
            'subjectivity_score': self._calculate_subjectivity(doc),
            'emotional_language': self._detect_emotional_language(doc),
            'overall_bias_score': 0.0  # Will be calculated
        }
        
        analysis['overall_bias_score'] = self._calculate_overall_bias(analysis)
        
        return analysis
    
    def _analyze_sentiment(self, text):
        sentences = sent_tokenize(text)
        sentiments = []
        
        for sentence in sentences:
            scores = self.sid.polarity_scores(sentence)
            sentiments.append(scores)
            
        avg_sentiment = {
            'compound': np.mean([s['compound'] for s in sentiments]),
            'pos': np.mean([s['pos'] for s in sentiments]),
            'neg': np.mean([s['neg'] for s in sentiments]),
            'neu': np.mean([s['neu'] for s in sentiments])
        }
        
        return avg_sentiment
    
    def _calculate_subjectivity(self, doc):
        subjective_words = 0
        total_words = len([token for token in doc if not token.is_punct])
        
        for token in doc:
            if (token.pos_ in ['ADJ', 'ADV'] or 
                token.lemma_ in self.opinion_words or 
                token.lemma_ in self.extreme_words):
                subjective_words += 1
        
        return subjective_words / total_words if total_words > 0 else 0
    
    def _detect_emotional_language(self, doc):
        emotional_phrases = []
        
        for sent in doc.sents:
            scores = self.sid.polarity_scores(sent.text)
            if abs(scores['compound']) > 0.5:  
                emotional_phrases.append({
                    'text': sent.text,
                    'intensity': scores['compound']
                })
        
        return emotional_phrases
    
    def _calculate_overall_bias(self, analysis):
        sentiment_weight = 0.3
        subjectivity_weight = 0.3
        emotional_weight = 0.2
        indicators_weight = 0.2
        
        sentiment_score = abs(analysis['sentiment_scores']['compound'])
        subjectivity_score = analysis['subjectivity_score']
        emotional_score = len(analysis['emotional_language']) / 10  
        indicators_score = sum(len(v) for v in analysis['bias_indicators'].values()) / 10
        
        overall_score = (
            sentiment_score * sentiment_weight +
            subjectivity_score * subjectivity_weight +
            min(emotional_score, 1.0) * emotional_weight +
            min(indicators_score, 1.0) * indicators_weight
        )
        
        return min(overall_score * 5, 5.0)
