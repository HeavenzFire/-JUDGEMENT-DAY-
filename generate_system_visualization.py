#!/usr/bin/env python3
"""
System Visualization Generator for SAOS (Syntropic Agent Operating System)

This script generates visual representations of the system components and their relationships.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
import os

def create_component_overview_chart():
    """Create a bar chart showing system components and their status."""

    # System components data
    components = [
        'SAOS Core', 'Harm System Tracer', 'Grounded Ethical Framework',
        'Emotional Entropy Detector', 'Resonance Engine', 'UNCAGE Distribution',
        'Syntropic Shield', 'Guardian OS', 'Harm Reduction Engine',
        'Communication Grounding'
    ]

    # Status values (0-1 scale representing completion/readiness)
    status = [0.95, 0.90, 0.85, 0.80, 0.88, 0.92, 0.87, 0.93, 0.89, 0.86]

    # Colors based on status
    colors = ['#2E8B57' if s >= 0.9 else '#FFD700' if s >= 0.8 else '#FF6347' for s in status]

    fig, ax = plt.subplots(figsize=(12, 8))

    bars = ax.barh(components, status, color=colors, alpha=0.8)

    # Add value labels on bars
    for bar, val in zip(bars, status):
        ax.text(val + 0.01, bar.get_y() + bar.get_height()/2,
                f'{val:.2f}', ha='left', va='center', fontweight='bold')

    ax.set_xlim(0, 1.1)
    ax.set_xlabel('Readiness Status', fontsize=12, fontweight='bold')
    ax.set_title('SAOS System Components Overview', fontsize=16, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)

    # Add legend
    legend_elements = [
        plt.Rectangle((0,0),1,1, facecolor='#2E8B57', alpha=0.8, label='Production Ready (≥0.9)'),
        plt.Rectangle((0,0),1,1, facecolor='#FFD700', alpha=0.8, label='Beta Stage (0.8-0.89)'),
        plt.Rectangle((0,0),1,1, facecolor='#FF6347', alpha=0.8, label='Development (<0.8)')
    ]
    ax.legend(handles=legend_elements, loc='lower right')

    plt.tight_layout()
    plt.savefig('/vercel/sandbox/system_components_overview.png', dpi=300, bbox_inches='tight')
    plt.close()

    return '/vercel/sandbox/system_components_overview.png'

def create_system_architecture_diagram():
    """Create a network diagram showing system relationships."""

    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Define component positions and properties
    components = {
        'SAOS Core': {'pos': (7, 9), 'color': '#4CAF50', 'size': (2.5, 1)},
        'Harm System Tracer': {'pos': (2, 7), 'color': '#2196F3', 'size': (2.2, 0.8)},
        'Grounded Ethical Framework': {'pos': (12, 7), 'color': '#FF9800', 'size': (2.2, 0.8)},
        'Emotional Entropy Detector': {'pos': (2, 5), 'color': '#9C27B0', 'size': (2.2, 0.8)},
        'Resonance Engine': {'pos': (12, 5), 'color': '#607D8B', 'size': (2.2, 0.8)},
        'UNCAGE Distribution': {'pos': (4, 3), 'color': '#795548', 'size': (2.2, 0.8)},
        'Syntropic Shield': {'pos': (10, 3), 'color': '#E91E63', 'size': (2.2, 0.8)},
        'Guardian OS': {'pos': (1, 1), 'color': '#00BCD4', 'size': (2.2, 0.8)},
        'Harm Reduction Engine': {'pos': (7, 1), 'color': '#8BC34A', 'size': (2.2, 0.8)},
        'Communication Grounding': {'pos': (13, 1), 'color': '#FFC107', 'size': (2.2, 0.8)}
    }

    # Draw components
    for name, props in components.items():
        x, y = props['pos']
        w, h = props['size']

        # Create rounded rectangle
        rect = FancyBboxPatch((x-w/2, y-h/2), w, h,
                            boxstyle="round,pad=0.05",
                            facecolor=props['color'],
                            edgecolor='black',
                            linewidth=2)
        ax.add_patch(rect)

        # Add text
        ax.text(x, y, name, ha='center', va='center',
                fontsize=9, fontweight='bold', wrap=True)

    # Draw connections
    connections = [
        ('SAOS Core', 'Harm System Tracer'),
        ('SAOS Core', 'Grounded Ethical Framework'),
        ('SAOS Core', 'Emotional Entropy Detector'),
        ('SAOS Core', 'Resonance Engine'),
        ('Harm System Tracer', 'Harm Reduction Engine'),
        ('Grounded Ethical Framework', 'Communication Grounding'),
        ('Emotional Entropy Detector', 'Guardian OS'),
        ('Resonance Engine', 'Syntropic Shield'),
        ('UNCAGE Distribution', 'Guardian OS'),
        ('UNCAGE Distribution', 'Harm Reduction Engine'),
        ('Syntropic Shield', 'Communication Grounding')
    ]

    for comp1, comp2 in connections:
        pos1 = components[comp1]['pos']
        pos2 = components[comp2]['pos']

        # Create connection line
        con = ConnectionPatch(pos1, pos2, "data", "data",
                            arrowstyle="->", shrinkA=30, shrinkB=30,
                            mutation_scale=15, fc="black", color="black",
                            linewidth=1.5, alpha=0.7)
        ax.add_artist(con)

    # Add title
    ax.text(7, 9.5, 'SAOS System Architecture',
            ha='center', va='center', fontsize=16, fontweight='bold')

    # Add legend
    legend_x, legend_y = 0.02, 0.02
    ax.text(legend_x, legend_y + 0.15, 'Legend:', fontsize=12, fontweight='bold',
            transform=ax.transAxes)

    legend_items = [
        ('Core Systems', '#4CAF50'),
        ('Analysis Tools', '#2196F3'),
        ('Ethical Frameworks', '#FF9800'),
        ('Monitoring', '#9C27B0'),
        ('Coordination', '#607D8B'),
        ('Distribution', '#795548'),
        ('Protection', '#E91E63'),
        ('Deployment', '#00BCD4'),
        ('Action', '#8BC34A'),
        ('Communication', '#FFC107')
    ]

    for i, (label, color) in enumerate(legend_items):
        y_pos = legend_y + 0.12 - i * 0.015
        rect = plt.Rectangle((legend_x, y_pos), 0.02, 0.01,
                           facecolor=color, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(legend_x + 0.025, y_pos + 0.005, label,
                fontsize=8, transform=ax.transAxes)

    plt.savefig('/vercel/sandbox/system_architecture_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()

    return '/vercel/sandbox/system_architecture_diagram.png'

def create_system_evolution_timeline():
    """Create a timeline showing system evolution."""

    fig, ax = plt.subplots(figsize=(12, 8))

    # Timeline data
    phases = [
        'HeavenzFire-OS\n(Initial)',
        'Syntropic\nIntegration',
        'Ethical\nFrameworks',
        'Distribution\n& Scale',
        'Harm Reduction\n& Communication',
        'Current SAOS\nSystem'
    ]

    dates = ['2023', '2024', '2024', '2025', '2025', '2026']
    y_positions = [1, 2, 3, 4, 5, 6]

    # Plot timeline
    ax.plot([0.1, 0.9], [1, 6], 'k-', alpha=0.3, linewidth=2)

    # Add phase markers
    for i, (phase, date, y) in enumerate(zip(phases, dates, y_positions)):
        ax.scatter(0.5, y, s=200, c='#4CAF50', alpha=0.8, edgecolors='black', linewidth=2)
        ax.text(0.5, y + 0.1, phase, ha='center', va='bottom',
                fontsize=10, fontweight='bold', wrap=True)
        ax.text(0.5, y - 0.1, date, ha='center', va='top',
                fontsize=9, style='italic')

    # Add key achievements
    achievements = [
        'Entangled Multimodal System\n+ Dragon Mesh P2P',
        'Resonance coordination\n+ Swarm intelligence',
        'Harm tracing + Grounded ethics',
        'UNCAGE P2P + Browser extensions',
        'Measurable interventions\n+ Communication tools',
        'Complete SAOS framework\n+ Field deployment ready'
    ]

    for i, achievement in enumerate(achievements):
        ax.text(0.75, y_positions[i], achievement, fontsize=8,
                verticalalignment='center', bbox=dict(boxstyle="round,pad=0.3",
                facecolor='lightblue', alpha=0.5))

    ax.set_xlim(0, 1)
    ax.set_ylim(0.5, 6.5)
    ax.axis('off')
    ax.set_title('SAOS System Evolution Timeline', fontsize=16, fontweight='bold', pad=20)

    plt.savefig('/vercel/sandbox/system_evolution_timeline.png', dpi=300, bbox_inches='tight')
    plt.close()

    return '/vercel/sandbox/system_evolution_timeline.png'

def main():
    """Generate all system visualizations."""

    print("Generating system visualizations...")

    # Create output directory if it doesn't exist
    os.makedirs('/vercel/sandbox', exist_ok=True)

    # Generate visualizations
    overview_path = create_component_overview_chart()
    print(f"✓ Generated component overview: {overview_path}")

    architecture_path = create_system_architecture_diagram()
    print(f"✓ Generated architecture diagram: {architecture_path}")

    timeline_path = create_system_evolution_timeline()
    print(f"✓ Generated evolution timeline: {timeline_path}")

    print("\nAll visualizations generated successfully!")
    print("Files saved:")
    print(f"  - {overview_path}")
    print(f"  - {architecture_path}")
    print(f"  - {timeline_path}")

if __name__ == "__main__":
    main()