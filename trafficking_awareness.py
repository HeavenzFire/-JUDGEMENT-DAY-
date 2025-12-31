#!/usr/bin/env python3
"""
Human Trafficking Awareness Tool
Provides statistics, facts, and educational materials to raise awareness about human trafficking.
All information sourced from verified organizations like the UN, Polaris Project, and ILO.
"""

import json
import datetime

class TraffickingAwareness:
    def __init__(self):
        self.stats = self._load_statistics()
        self.facts = self._load_facts()

    def _load_statistics(self):
        """Load verified statistics from reliable sources"""
        return {
            "global_trafficking": {
                "victims": "Approximately 50 million people worldwide are victims of modern slavery",
                "source": "International Labour Organization (ILO) and Walk Free Foundation",
                "year": 2021
            },
            "sex_trafficking": {
                "percentage": "About 25% of all trafficking victims are trafficked for sexual exploitation",
                "source": "United Nations Office on Drugs and Crime (UNODC)",
                "year": 2022
            },
            "children": {
                "percentage": "Around 28% of detected trafficking victims are children",
                "source": "UNODC Global Report on Trafficking in Persons",
                "year": 2022
            },
            "economic_impact": {
                "amount": "$150 billion annually in illegal profits",
                "source": "ILO",
                "year": 2021
            }
        }

    def _load_facts(self):
        """Load important facts about human trafficking"""
        return [
            "Human trafficking can happen to anyone, regardless of age, gender, or background.",
            "Traffickers often use force, fraud, or coercion to control their victims.",
            "Online platforms are increasingly used for recruitment and exploitation.",
            "Many victims are trafficked by someone they know and trust.",
            "Human trafficking is a hidden crime - victims are often not visible in plain sight.",
            "Recovery and rehabilitation support is crucial for survivors.",
            "Education and awareness are key to prevention.",
            "Reporting suspicious activity can save lives."
        ]

    def display_statistics(self):
        """Display current statistics"""
        print("=" * 60)
        print("HUMAN TRAFFICKING STATISTICS")
        print("=" * 60)
        print(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        for category, data in self.stats.items():
            print(f"📊 {category.replace('_', ' ').title()}:")
            print(f"   {data['victims'] if 'victims' in data else data['percentage'] if 'percentage' in data else data['amount']}")
            print(f"   Source: {data['source']} ({data['year']})")
            print()

    def display_facts(self):
        """Display important facts"""
        print("=" * 60)
        print("IMPORTANT FACTS ABOUT HUMAN TRAFFICKING")
        print("=" * 60)

        for i, fact in enumerate(self.facts, 1):
            print(f"{i}. {fact}")
        print()

    def generate_awareness_message(self):
        """Generate a shareable awareness message"""
        message = """
🚨 HUMAN TRAFFICKING AWARENESS 🚨

Did you know?
- 50 million people worldwide are victims of modern slavery
- 1 in 4 trafficking victims are exploited sexually
- Many victims are trafficked by people they know

Human trafficking is happening in every country. It can happen to anyone.

If you suspect trafficking:
- Call the National Human Trafficking Hotline: 1-888-373-7888 (US)
- Or text "HELP" to 233733
- Report online at humantraffickinghotline.org

Together, we can end human trafficking.
#EndHumanTrafficking #StopTrafficking
        """
        return message.strip()

    def run_education_session(self):
        """Run an interactive education session"""
        print("Welcome to the Human Trafficking Awareness Education Session")
        print("=" * 60)

        self.display_statistics()
        input("Press Enter to continue...")

        self.display_facts()
        input("Press Enter to continue...")

        print("SHAREABLE AWARENESS MESSAGE:")
        print("-" * 40)
        print(self.generate_awareness_message())
        print("-" * 40)

        print("\nRemember: Awareness is the first step toward prevention.")
        print("If you need help or want to get involved, contact local anti-trafficking organizations.")

def main():
    awareness = TraffickingAwareness()
    awareness.run_education_session()

if __name__ == "__main__":
    main()