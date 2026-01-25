#!/usr/bin/env python3
"""
Leadership, Resilience, and Inspirational Narratives

This module implements the leadership and inspirational core of the thesis, including:
- What a 15-Year-Old Meth Addict Taught Me About Leadership | Brian Fretwell | TEDxBoise
"""

from typing import Dict, Any, List


class TEDTalkLeadership:
    """
    What a 15-Year-Old Meth Addict Taught Me About Leadership | Brian Fretwell | TEDxBoise

    This TED Talk recounts lessons from a young addict, highlighting themes of empathy,
    redemption, and unconventional wisdom. Leadership involves seeing potential in the broken,
    fostering resilience.
    """

    def __init__(self):
        """Initialize the TED Talk leadership lesson."""
        self.leadership_lessons = []
        self.resilience_factors = []

    def get_leadership_lesson(self) -> Dict[str, Any]:
        """
        Get the leadership lesson from the TED Talk.

        Returns:
            Dictionary containing the leadership lesson
        """
        # Core story elements
        story_elements = {
            "protagonist": "15-year-old meth addict",
            "teacher": "Brian Fretwell (speaker)",
            "setting": "TEDxBoise",
            "key_revelation": "True leadership comes from seeing potential in the most broken places"
        }

        # Extracted lessons
        lessons = [
            {
                "lesson": "Authentic leadership requires vulnerability and honesty",
                "source": "The addict's raw honesty about his struggles",
                "application": "Leaders must be willing to confront their own flaws"
            },
            {
                "lesson": "Potential exists in everyone, regardless of circumstances",
                "source": "Finding wisdom in someone society has discarded",
                "application": "Never write people off based on their current situation"
            },
            {
                "lesson": "True change requires facing reality without illusions",
                "source": "The addict's clear-eyed view of his addiction",
                "application": "Leadership demands uncomfortable truths over comfortable lies"
            },
            {
                "lesson": "Resilience comes from embracing, not avoiding, pain",
                "source": "The addict's journey through recovery",
                "application": "Growth happens at the edge of discomfort"
            }
        ]

        # Calculate leadership impact
        impact_score = self._calculate_leadership_impact(lessons)

        # Generate resilience factors
        resilience_factors = self._generate_resilience_factors()

        leadership_lesson = {
            "story_elements": story_elements,
            "core_lessons": lessons,
            "leadership_impact": impact_score,
            "resilience_factors": resilience_factors,
            "key_takeaway": "Leadership is not about perfection; it's about seeing and nurturing the potential for redemption in everyone, including ourselves",
            "ai_correlation": "AI systems could learn from this approach, developing 'empathic leadership' capabilities that see potential in flawed data and guide systems toward redemption rather than rejection"
        }

        self.leadership_lessons.append(leadership_lesson)
        return leadership_lesson

    def _calculate_leadership_impact(self, lessons: List[Dict[str, Any]]) -> float:
        """Calculate the leadership impact score."""
        base_impact = 0.85
        lesson_depth = len(lessons) * 0.05  # More lessons = deeper impact
        authenticity_factor = 0.92  # High authenticity from real story
        applicability_bonus = 0.08  # Highly applicable to real leadership

        return min(1.0, base_impact + lesson_depth + authenticity_factor * 0.1 + applicability_bonus)

    def _generate_resilience_factors(self) -> List[Dict[str, Any]]:
        """Generate resilience factors from the leadership lesson."""
        factors = [
            {
                "factor": "Vulnerability as Strength",
                "description": "Embracing personal flaws builds authentic connection",
                "strength": 0.88
            },
            {
                "factor": "Potential Recognition",
                "description": "Seeing possibility where others see only brokenness",
                "strength": 0.91
            },
            {
                "factor": "Truth Confrontation",
                "description": "Facing uncomfortable realities without illusion",
                "strength": 0.94
            },
            {
                "factor": "Redemptive Growth",
                "description": "Finding wisdom and strength through struggle",
                "strength": 0.89
            }
        ]

        self.resilience_factors.extend(factors)
        return factors


class LeadershipNarratives:
    """
    Main class containing all leadership and inspirational narratives.
    """

    def __init__(self):
        """Initialize all leadership narratives."""
        self.ted_talk = TEDTalkLeadership()