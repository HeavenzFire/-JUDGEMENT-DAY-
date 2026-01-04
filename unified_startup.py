#!/usr/bin/env python3
"""
Unified Startup Script
Starts all systems and integrations in the correct order.
"""

import logging
import time
import signal
import sys
from master_orchestrator import orchestrator
from cross_system_communication import initialize_communication
from system_integration_layer import initialize_integration
from unified_system_dashboard import dashboard

logger = logging.getLogger(__name__)

class UnifiedSystem:
    """Unified system that starts and manages all components."""

    def __init__(self):
        self.running = False
        self.components = []

    def initialize_components(self):
        """Initialize all system components in order."""
        logger.info("Initializing unified system components...")

        try:
            # 1. Initialize communication system
            initialize_communication()
            self.components.append("communication")
            logger.info("✓ Communication system initialized")

            # 2. Initialize integration layer
            initialize_integration()
            self.components.append("integration")
            logger.info("✓ Integration layer initialized")

            # 3. Start master orchestrator
            orchestrator.start()
            self.components.append("orchestrator")
            logger.info("✓ Master orchestrator started")

            # 4. Start dashboard (optional, in background)
            try:
                import threading
                dashboard_thread = threading.Thread(target=dashboard.start, daemon=True)
                dashboard_thread.start()
                self.components.append("dashboard")
                logger.info("✓ Dashboard started on http://0.0.0.0:8080")
            except Exception as e:
                logger.warning(f"Dashboard failed to start: {e}")

            logger.info("All components initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            self.shutdown()
            return False

    def start(self):
        """Start the unified system."""
        logger.info("Starting unified system...")

        if not self.initialize_components():
            return False

        self.running = True
        logger.info("🎉 Unified system is now running!")
        logger.info("Available systems:")
        for name, info in orchestrator.systems.items():
            logger.info(f"  - {name}: {info.status}")

        logger.info("\n🌐 System URLs:")
        logger.info("  - Dashboard: http://localhost:8080")
        logger.info("  - API: http://localhost:8080/api/")

        # Keep running until shutdown
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        finally:
            self.shutdown()

    def shutdown(self):
        """Shutdown all components gracefully."""
        logger.info("Shutting down unified system...")

        # Stop components in reverse order
        if "dashboard" in self.components:
            dashboard.stop()
            logger.info("✓ Dashboard stopped")

        if "orchestrator" in self.components:
            orchestrator.stop()
            logger.info("✓ Orchestrator stopped")

        self.running = False
        logger.info("✓ Unified system shutdown complete")

    def get_status(self) -> dict:
        """Get overall system status."""
        return {
            "running": self.running,
            "components": self.components,
            "systems": orchestrator.get_system_status(),
            "mesh_status": orchestrator.data_flow_manager.get_mesh_status() if hasattr(orchestrator, 'data_flow_manager') else {},
            "timestamp": time.time()
        }

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    unified_system.running = False

# Global unified system instance
unified_system = UnifiedSystem()

def main():
    """Main entry point."""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/tmp/unified_system.log')
        ]
    )

    logger.info("🚀 Starting Unified System v1.0")
    logger.info("=" * 50)

    try:
        unified_system.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        unified_system.shutdown()
        sys.exit(1)

if __name__ == "__main__":
    main()