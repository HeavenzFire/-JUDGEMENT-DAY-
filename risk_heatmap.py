import matplotlib.pyplot as plt
import numpy as np
import json
import os
from datetime import datetime

class RiskHeatmapGenerator:
    """
    Generates real-time risk heatmaps from ZFIRE OS swarm data
    """

    def __init__(self):
        self.domains = [
            'Environmental & Climate',
            'Biosecurity',
            'Atmospheric / Geophysical',
            'AI Alignment / System Integrity',
            'Geopolitical / External Signals'
        ]

        # Simulated risk data based on swarm reports
        self.risk_data = {
            'Environmental & Climate': {
                'risk_level': 0.37,
                'acceleration': 0.15,
                'indicators': ['Temperature fluctuations', 'Humidity anomalies', 'Air quality shifts']
            },
            'Biosecurity': {
                'risk_level': 0.55,
                'acceleration': 0.20,
                'indicators': ['Pathogen conditions', 'Risk gradient acceleration']
            },
            'Atmospheric / Geophysical': {
                'risk_level': 0.25,
                'acceleration': 0.10,
                'indicators': ['Pressure fluctuations', 'Electromagnetic anomalies']
            },
            'AI Alignment / System Integrity': {
                'risk_level': 0.15,
                'acceleration': 0.07,
                'indicators': ['Computation drift', 'Latency surges']
            },
            'Geopolitical / External Signals': {
                'risk_level': 0.60,
                'acceleration': 0.25,
                'indicators': ['Conflict indicators', 'Resource tension']
            }
        }

    def generate_heatmap(self, output_file='risk_heatmap.png'):
        """
        Generate dual-panel risk heatmap showing risk levels and acceleration
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Prepare data for heatmaps
        risk_levels = [self.risk_data[domain]['risk_level'] for domain in self.domains]
        accelerations = [self.risk_data[domain]['acceleration'] for domain in self.domains]

        # Create 2D arrays for heatmap (single row for simplicity)
        risk_matrix = np.array([risk_levels])
        accel_matrix = np.array([accelerations])

        # Risk Level Heatmap
        im1 = ax1.imshow(risk_matrix, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=1)
        ax1.set_title('Risk Levels by Domain', fontsize=14, fontweight='bold')
        ax1.set_xticks(range(len(self.domains)))
        ax1.set_xticklabels([d.split(' / ')[0] for d in self.domains], rotation=45, ha='right')
        ax1.set_yticks([])
        plt.colorbar(im1, ax=ax1, label='Risk Level (0-1)')

        # Add risk level values on heatmap
        for i, (domain, risk) in enumerate(zip(self.domains, risk_levels)):
            ax1.text(i, 0, f'{risk:.2f}', ha='center', va='center',
                    color='white' if risk > 0.5 else 'black', fontweight='bold')

        # Acceleration Heatmap
        im2 = ax2.imshow(accel_matrix, cmap='OrRd', aspect='auto', vmin=0, vmax=0.3)
        ax2.set_title('Acceleration Patterns', fontsize=14, fontweight='bold')
        ax2.set_xticks(range(len(self.domains)))
        ax2.set_xticklabels([d.split(' / ')[0] for d in self.domains], rotation=45, ha='right')
        ax2.set_yticks([])
        plt.colorbar(im2, ax=ax2, label='Acceleration Rate')

        # Add acceleration values on heatmap
        for i, (domain, accel) in enumerate(zip(self.domains, accelerations)):
            ax2.text(i, 0, f'{accel:.2f}', ha='center', va='center',
                    color='white' if accel > 0.15 else 'black', fontweight='bold')

        # Overall title
        fig.suptitle(f'ZFIRE OS Risk Heatmap - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                    fontsize=16, fontweight='bold', y=0.98)

        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()

        return output_file

    def get_risk_summary(self):
        """
        Generate text summary of risk analysis
        """
        total_risk = sum([self.risk_data[d]['risk_level'] for d in self.domains]) / len(self.domains)
        max_risk_domain = max(self.risk_data.keys(), key=lambda x: self.risk_data[x]['risk_level'])
        alerts = [domain for domain in self.domains if self.risk_data[domain]['acceleration'] > 0.15]

        return {
            'overall_risk': round(total_risk, 2),
            'highest_risk_domain': max_risk_domain,
            'active_alerts': len(alerts),
            'alert_domains': alerts
        }

if __name__ == "__main__":
    generator = RiskHeatmapGenerator()

    # Generate heatmap
    output_file = generator.generate_heatmap()
    print(f"Risk heatmap generated: {output_file}")

    # Print summary
    summary = generator.get_risk_summary()
    print("\n=== ZFIRE OS Risk Analysis Summary ===")
    print(f"Overall Risk Score: {summary['overall_risk']}")
    print(f"Highest Risk Domain: {summary['highest_risk_domain']}")
    print(f"Active Acceleration Alerts: {summary['active_alerts']}")
    if summary['alert_domains']:
        print("Alert Domains:")
        for domain in summary['alert_domains']:
            print(f"  - {domain}: +{generator.risk_data[domain]['acceleration']:.2f} acceleration")