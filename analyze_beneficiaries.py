#!/usr/bin/env python3
"""
Beneficiaries Analysis Script
Analyzes the beneficiaries_list.csv to understand the distribution and patterns
of beneficiaries in the harm reduction system.
"""

import pandas as pd
import json
import os
from collections import Counter, defaultdict
from datetime import datetime

def load_and_analyze_data():
    """Phase 1: Load complete file and discover structure"""
    print("Phase 1: Loading beneficiaries data...")

    # Read the CSV file
    df = pd.read_csv('/vercel/sandbox/beneficiaries_list.csv')

    print(f"Loaded {len(df)} beneficiaries")
    print(f"Columns: {list(df.columns)}")

    # Basic structure analysis
    structure = {
        'total_beneficiaries': len(df),
        'columns': list(df.columns),
        'data_types': df.dtypes.to_dict(),
        'null_counts': df.isnull().sum().to_dict(),
        'unique_values': {col: df[col].nunique() for col in df.columns}
    }

    return df, structure

def deep_analysis(df, structure):
    """Phase 2: Deep analysis of patterns and statistics"""
    print("Phase 2: Performing deep analysis...")

    analysis = {
        'timestamp': datetime.now().isoformat(),
        'structure': structure
    }

    # Location analysis
    if 'location' in df.columns:
        location_counts = df['location'].value_counts().to_dict()
        analysis['location_distribution'] = location_counts
        analysis['unique_locations'] = len(location_counts)

    # Email domain analysis
    if 'email' in df.columns:
        df['email_domain'] = df['email'].str.split('@').str[1]
        domain_counts = df['email_domain'].value_counts().to_dict()
        analysis['email_domains'] = domain_counts

    # Name analysis (basic patterns)
    if 'name' in df.columns:
        name_lengths = df['name'].str.len().describe().to_dict()
        analysis['name_statistics'] = name_lengths

        # Check for common name patterns
        first_names = df['name'].str.split().str[0]
        last_names = df['name'].str.split().str[-1]
        analysis['first_name_sample'] = first_names.head(5).tolist()
        analysis['last_name_sample'] = last_names.head(5).tolist()

    # Geographic insights
    analysis['geographic_insights'] = {
        'us_based': 'USA' in str(df.get('location', '')),
        'international': len(df.get('location', pd.Series()).unique()) > 1
    }

    return analysis

def detect_patterns_and_groupings(df, analysis):
    """Phase 3: Detect structure changes and find groupings"""
    print("Phase 3: Detecting patterns and groupings...")

    patterns = {
        'data_quality': {},
        'distribution_patterns': {},
        'risk_indicators': {}
    }

    # Data quality checks
    patterns['data_quality'] = {
        'complete_records': df.dropna().shape[0],
        'incomplete_records': df.isnull().any(axis=1).sum(),
        'duplicate_emails': df['email'].duplicated().sum() if 'email' in df.columns else 0,
        'duplicate_names': df['name'].duplicated().sum() if 'name' in df.columns else 0
    }

    # Distribution patterns
    if 'location' in df.columns:
        patterns['distribution_patterns']['location_concentration'] = (
            df['location'].value_counts().max() / len(df) * 100
        )

    # Risk indicators for harm reduction system
    patterns['risk_indicators'] = {
        'single_location_risk': len(df.get('location', pd.Series()).unique()) == 1,
        'small_beneficiary_pool': len(df) < 10,
        'geographic_diversity': len(df.get('location', pd.Series()).unique()) > 1
    }

    analysis['patterns'] = patterns
    return analysis

def save_insights(analysis):
    """Phase 4: Save insights to JSON"""
    print("Phase 4: Saving insights...")

    output_file = '/vercel/sandbox/beneficiaries_insights.json'
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)

    print(f"Insights saved to {output_file}")
    return output_file

def main():
    """Main analysis pipeline"""
    print("=== BENEFICIARIES ANALYSIS ===")
    print("Analyzing harm reduction system beneficiaries...")

    # Phase 1: Load and discover structure
    df, structure = load_and_analyze_data()

    # Phase 2: Deep analysis
    analysis = deep_analysis(df, structure)

    # Phase 3: Detect patterns
    analysis = detect_patterns_and_groupings(df, analysis)

    # Phase 4: Save insights
    output_file = save_insights(analysis)

    print("Analysis complete!")
    print(f"Total beneficiaries: {analysis['structure']['total_beneficiaries']}")
    print(f"Locations covered: {analysis.get('unique_locations', 'N/A')}")
    print(f"Data quality: {analysis['patterns']['data_quality']['complete_records']} complete records")

    return analysis

if __name__ == "__main__":
    analysis_results = main()