"""Sentiment Analysis Agent"""
from agents.base_agent import BaseAgent
from typing import Dict, Any, List
import re
import logging

logger = logging.getLogger(__name__)

class SentimentAgent(BaseAgent):
    def __init__(self):
        super().__init__("Sentiment Agent", "sentiment")
        self.sentiment_lexicon = self._load_lexicon()

    def _load_lexicon(self) -> Dict[str, float]:
        return {
            'bullish': 0.8, 'buy': 0.6, 'strong': 0.5, 'growth': 0.4, 'profit': 0.5,
            'gain': 0.4, 'upgrade': 0.7, 'beat': 0.6, 'surge': 0.7, 'rally': 0.6,
            'bearish': -0.8, 'sell': -0.6, 'weak': -0.5, 'decline': -0.4, 'loss': -0.5,
            'drop': -0.4, 'downgrade': -0.7, 'miss': -0.6, 'plunge': -0.7, 'crash': -0.8
        }

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        news_articles = input_data.get('news', [])

        if not news_articles:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'articles_analyzed': 0
            }

        sentiments = []
        for article in news_articles:
            text = article.get('title', '') + ' ' + article.get('summary', '')
            score = self._analyze_text(text)
            sentiments.append(score)

        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0

        return {
            'overall_sentiment': self._classify_sentiment(avg_sentiment),
            'sentiment_score': avg_sentiment,
            'confidence': min(len(sentiments) / 10, 1.0),
            'articles_analyzed': len(sentiments),
            'distribution': self._get_distribution(sentiments)
        }

    def _analyze_text(self, text: str) -> float:
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)

        scores = []
        for word in words:
            if word in self.sentiment_lexicon:
                scores.append(self.sentiment_lexicon[word])

        return sum(scores) / len(scores) if scores else 0.0

    def _classify_sentiment(self, score: float) -> str:
        if score >= 0.3:
            return 'positive'
        elif score <= -0.3:
            return 'negative'
        return 'neutral'

    def _get_distribution(self, sentiments: List[float]) -> Dict[str, int]:
        return {
            'positive': sum(1 for s in sentiments if s > 0.1),
            'neutral': sum(1 for s in sentiments if -0.1 <= s <= 0.1),
            'negative': sum(1 for s in sentiments if s < -0.1)
        }
