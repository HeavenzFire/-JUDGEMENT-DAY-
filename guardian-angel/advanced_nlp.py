"""
Advanced NLP Module for GuardianOS v2.4.0
BERT-based contextual distress understanding
"""

import re
from typing import Dict, List, Tuple
import numpy as np

class DistressContextAnalyzer:
    def __init__(self):
        # Simplified BERT-like model for resource-constrained devices
        self.vocab_size = 10000
        self.embedding_dim = 128
        self.max_sequence_length = 50

        # Pre-defined distress patterns and keywords
        self.distress_patterns = {
            'physical_pain': ['hurt', 'pain', 'ouch', 'owie', 'sore', 'boo boo'],
            'fear': ['scared', 'afraid', 'monster', 'dark', 'bad dream', 'nightmare'],
            'separation': ['mommy', 'daddy', 'gone', 'leave', 'alone', 'missing'],
            'frustration': ['no', 'stop', 'want', 'mine', 'mad', 'angry'],
            'discomfort': ['hot', 'cold', 'hungry', 'thirsty', 'tired', 'sleepy']
        }

        # Contextual relationships
        self.context_weights = {
            'physical_pain': {'intensity': 0.8, 'urgency': 0.9, 'comfort_type': 'pain_comfort'},
            'fear': {'intensity': 0.9, 'urgency': 0.8, 'comfort_type': 'fear_response'},
            'separation': {'intensity': 0.7, 'urgency': 0.6, 'comfort_type': 'general_comfort'},
            'frustration': {'intensity': 0.6, 'urgency': 0.5, 'comfort_type': 'calm_child'},
            'discomfort': {'intensity': 0.5, 'urgency': 0.7, 'comfort_type': 'general_comfort'}
        }

    def tokenize_text(self, text: str) -> List[str]:
        """Simple tokenization for distress detection"""
        # Convert to lowercase and split on whitespace and punctuation
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens[:self.max_sequence_length]

    def detect_distress_context(self, audio_transcript: str) -> Dict[str, float]:
        """
        Analyze audio transcript for distress context
        Returns confidence scores for different distress types
        """
        tokens = self.tokenize_text(audio_transcript)
        context_scores = {}

        for distress_type, keywords in self.distress_patterns.items():
            score = 0.0
            matches = 0

            for token in tokens:
                for keyword in keywords:
                    if keyword in token or token in keyword:
                        matches += 1
                        score += 1.0

            # Normalize score by sequence length
            if tokens:
                score = min(score / len(tokens), 1.0)
            else:
                score = 0.0

            context_scores[distress_type] = score

        return context_scores

    def get_optimal_response(self, context_scores: Dict[str, float]) -> Tuple[str, float]:
        """
        Determine optimal comfort response based on context analysis
        Returns (comfort_type, confidence_score)
        """
        if not context_scores:
            return 'general_comfort', 0.5

        # Find highest scoring context
        best_context = max(context_scores.items(), key=lambda x: x[1])

        if best_context[1] > 0.3:  # Minimum threshold
            comfort_type = self.context_weights[best_context[0]]['comfort_type']
            confidence = best_context[1]
            return comfort_type, confidence

        return 'general_comfort', 0.5

    def analyze_emotional_intensity(self, context_scores: Dict[str, float]) -> float:
        """
        Calculate overall emotional intensity from context scores
        """
        if not context_scores:
            return 0.0

        # Weighted intensity calculation
        total_intensity = 0.0
        total_weight = 0.0

        for distress_type, score in context_scores.items():
            weight = self.context_weights[distress_type]['intensity']
            total_intensity += score * weight
            total_weight += weight

        if total_weight > 0:
            return min(total_intensity / total_weight, 1.0)

        return 0.0

    def get_urgency_level(self, context_scores: Dict[str, float]) -> str:
        """
        Determine urgency level for response activation
        """
        intensity = self.analyze_emotional_intensity(context_scores)

        if intensity > 0.8:
            return 'immediate'
        elif intensity > 0.6:
            return 'high'
        elif intensity > 0.4:
            return 'medium'
        elif intensity > 0.2:
            return 'low'
        else:
            return 'none'