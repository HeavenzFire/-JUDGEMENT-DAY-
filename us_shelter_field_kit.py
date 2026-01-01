#!/usr/bin/env python3
"""
U.S. Shelter Field Kit v1.0
Comprehensive deployment package for domestic violence shelters in the U.S.

This kit provides everything needed for safe, effective deployment of GuardianOS
in U.S. domestic violence shelters, starting with Cleveland expansion.

Features:
- Hardware specifications and sourcing
- Step-by-step setup instructions
- Safety protocols and boundaries
- Support resources and contacts
- Anonymous feedback collection
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional

class ShelterFieldKit:
    """Manages the complete field kit for U.S. shelter deployments"""

    def __init__(self, version: str = "1.0"):
        self.version = version
        self.kit_path = "/opt/guardian_os/field_kit"
        self.hardware_specs = self._get_hardware_specs()
        self.setup_instructions = self._get_setup_instructions()
        self.safety_protocols = self._get_safety_protocols()
        self.support_resources = self._get_support_resources()

    def _get_hardware_specs(self) -> Dict:
        """Hardware requirements for U.S. shelter deployment"""
        return {
            "raspberry_pi": {
                "model": "Raspberry Pi Zero W",
                "ram": "512MB",
                "storage": "32GB microSD card (Class 10)",
                "power": "5V USB power adapter (2A)",
                "case": "Protective enclosure with ventilation",
                "microphone": "USB audio adapter with microphone",
                "speaker": "USB audio adapter with speaker (optional)"
            },
            "sourcing": {
                "recommended_vendors": ["Adafruit", "SparkFun", "Amazon"],
                "bulk_pricing_threshold": 10,
                "estimated_cost_per_unit": 75.00
            },
            "compatibility": {
                "os_version": "GuardianOS v2.0",
                "firmware_requirements": "Read-only root filesystem",
                "power_requirements": "Continuous power source"
            }
        }

    def _get_setup_instructions(self) -> List[Dict]:
        """Step-by-step setup instructions"""
        return [
            {
                "step": 1,
                "title": "Hardware Assembly",
                "description": "Connect Raspberry Pi Zero W to USB audio adapters",
                "time_estimate": "15 minutes",
                "tools_needed": ["Screwdriver", "USB cables"],
                "verification": "Test audio input/output with test tones"
            },
            {
                "step": 2,
                "title": "SD Card Imaging",
                "description": "Flash GuardianOS v2.0 image to microSD card",
                "time_estimate": "10 minutes",
                "tools_needed": ["SD card reader", "Imaging software"],
                "verification": "Verify checksum matches official release"
            },
            {
                "step": 3,
                "title": "Initial Configuration",
                "description": "Configure location and basic settings",
                "time_estimate": "5 minutes",
                "tools_needed": ["Keyboard", "Monitor"],
                "verification": "System boots and shows pictogram interface"
            },
            {
                "step": 4,
                "title": "Placement and Testing",
                "description": "Position device and test audio monitoring",
                "time_estimate": "10 minutes",
                "tools_needed": ["Test audio source"],
                "verification": "Device responds to test distress signals"
            }
        ]

    def _get_safety_protocols(self) -> Dict:
        """Safety protocols and boundaries for deployment"""
        return {
            "deployment_boundaries": {
                "never_deploy_in": [
                    "Bathrooms or private spaces",
                    "Areas with confidential conversations",
                    "Locations with existing surveillance",
                    "Spaces without caregiver consent"
                ],
                "always_deploy_with": [
                    "Written shelter coordinator approval",
                    "Staff training on system operation",
                    "Clear labeling of device purpose",
                    "Emergency shutdown procedures"
                ]
            },
            "ethical_considerations": {
                "data_collection": "None - system is offline and anonymous",
                "privacy_protection": "No recordings, no data transmission",
                "cultural_sensitivity": "Respects all cultural backgrounds",
                "trauma_informed": "Designed by child welfare experts"
            },
            "emergency_procedures": {
                "immediate_shutdown": "Hold power button for 5 seconds",
                "device_removal": "Physically disconnect power",
                "incident_reporting": "Contact local child welfare authorities",
                "system_reset": "Replace SD card with fresh image"
            }
        }

    def _get_support_resources(self) -> Dict:
        """Support resources for deployed systems"""
        return {
            "technical_support": {
                "email": "support@guardianos.org",
                "response_time": "24-48 hours",
                "anonymous_reporting": True
            },
            "training_resources": {
                "staff_training_guide": "Available in field kit",
                "video_tutorials": "Offline video files included",
                "pictogram_reference": "Universal symbol guide"
            },
            "community_resources": {
                "local_hotlines": {
                    "national_domestic_violence_hotline": "1-800-799-7233",
                    "childhelp_national_hotline": "1-800-4-A-CHILD"
                },
                "professional_networks": [
                    "National Coalition Against Domestic Violence",
                    "National Network to End Domestic Violence",
                    "Child Welfare League of America"
                ]
            },
            "feedback_collection": {
                "anonymous_feedback_form": "Included in field kit",
                "improvement_suggestions": "Collected quarterly",
                "outcome_tracking": "Optional anonymous reporting"
            }
        }

    def generate_field_kit_package(self, output_path: str) -> str:
        """Generate complete field kit package"""
        kit_data = {
            "version": self.version,
            "generated": datetime.now().isoformat(),
            "hardware_specs": self.hardware_specs,
            "setup_instructions": self.setup_instructions,
            "safety_protocols": self.safety_protocols,
            "support_resources": self.support_resources,
            "checksum": ""
        }

        # Generate checksum
        kit_json = json.dumps(kit_data, sort_keys=True, indent=2)
        kit_data["checksum"] = hashlib.sha256(kit_json.encode()).hexdigest()

        # Write to file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(kit_data, f, indent=2)

        return output_path

    def validate_kit_integrity(self, kit_path: str) -> bool:
        """Validate field kit integrity"""
        try:
            with open(kit_path, 'r') as f:
                kit_data = json.load(f)

            # Recalculate checksum
            temp_data = kit_data.copy()
            original_checksum = temp_data.pop("checksum")
            kit_json = json.dumps(temp_data, sort_keys=True, indent=2)
            calculated_checksum = hashlib.sha256(kit_json.encode()).hexdigest()

            return original_checksum == calculated_checksum
        except:
            return False

def main():
    """Generate U.S. Shelter Field Kit v1.0"""
    kit = ShelterFieldKit()

    output_path = "/opt/guardian_os/field_kit/us_shelter_kit_v1.0.json"
    generated_path = kit.generate_field_kit_package(output_path)

    print("U.S. Shelter Field Kit v1.0 Generated")
    print(f"Location: {generated_path}")
    print(f"Integrity: {'Valid' if kit.validate_kit_integrity(generated_path) else 'Invalid'}")

    # Display key information
    print("\nHardware Requirements:")
    hw = kit.hardware_specs["raspberry_pi"]
    print(f"- Raspberry Pi: {hw['model']}")
    print(f"- Storage: {hw['storage']}")
    print(f"- Estimated Cost: ${kit.hardware_specs['sourcing']['estimated_cost_per_unit']}")

    print("\nSafety Protocols:")
    for boundary in kit.safety_protocols["deployment_boundaries"]["always_deploy_with"]:
        print(f"- {boundary}")

    print("\nSupport Resources:")
    print(f"- Technical Support: {kit.support_resources['technical_support']['email']}")
    print(f"- National Hotline: {kit.support_resources['community_resources']['local_hotlines']['national_domestic_violence_hotline']}")

if __name__ == "__main__":
    main()