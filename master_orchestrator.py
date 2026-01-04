#!/usr/bin/env python3
"""
Master Orchestrator for All Systems and Creations
Connects and coordinates all independent systems in the ecosystem.
"""

import importlib
import inspect
import logging
import threading
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from queue import Queue
import json
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class SystemInfo:
    """Information about a registered system."""
    name: str
    module: str
    class_name: str
    instance: Any = None
    status: str = "uninitialized"
    dependencies: List[str] = None
    capabilities: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.capabilities is None:
            self.capabilities = []

class EventBus:
    """Event-driven message passing system for inter-system communication."""

    def __init__(self):
        self.subscribers: Dict[str, List[callable]] = {}
        self.event_queue = Queue()
        self.running = False
        self.worker_thread = None

    def subscribe(self, event_type: str, callback: callable):
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.info(f"Subscribed to event: {event_type}")

    def publish(self, event_type: str, data: Any = None):
        """Publish an event to all subscribers."""
        self.event_queue.put((event_type, data))
        logger.debug(f"Published event: {event_type}")

    def start(self):
        """Start the event processing thread."""
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_events)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        logger.info("Event bus started")

    def stop(self):
        """Stop the event processing thread."""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join()
        logger.info("Event bus stopped")

    def _process_events(self):
        """Process events from the queue."""
        while self.running:
            try:
                event_type, data = self.event_queue.get(timeout=1)
                if event_type in self.subscribers:
                    for callback in self.subscribers[event_type]:
                        try:
                            callback(data)
                        except Exception as e:
                            logger.error(f"Error in event callback: {e}")
                self.event_queue.task_done()
            except:
                continue

class MasterOrchestrator:
    """Master orchestrator connecting all systems and creations."""

    def __init__(self):
        self.systems: Dict[str, SystemInfo] = {}
        self.event_bus = EventBus()
        self.data_flow_manager = DataFlowManager(self)
        self.health_monitor = HealthMonitor(self)
        self.running = False
        self.system_thread = None

        # Auto-discover systems
        self._discover_systems()

    def _discover_systems(self):
        """Automatically discover available systems in the ecosystem."""
        system_modules = [
            'guardian_angel.guardian_runtime',
            'syntropic_weave',
            'constellation_mapper',
            'dragon_gossip_v2_1_final',
            'consciousness_bridge',
            'swarm_manager',
            'actuators',
            'cortex',
            'spirit',
            'resonance_core',
            'semantic_bus',
            'syntropic_agent_os',
            'living_evolution_system',
            'sovereign_truth_engine',
            'topological_kernel',
            'torsion_field',
            'nonlinear_simulation_engine',
            'embodied_swarm_simulation',
            'ready_player_one_world',
            'universal_potential_declaration',
            'nations_awakening_protocol',
            'participatory_elohim_protocol_v1',
            'single_node_declaration',
            'SCIN_RULES',
            'blood_moon_protocol',
            'breakthrough_inventory',
            'child_protection',
            'family_safety_coordinator',
            'trafficking_awareness',
            'weather_service',
            'banking_audit_visualizer',
            'concurrency_manager',
            'cortex',
            'heartbeat_page',
            'hz_kernel',
            'nodes',
            'omni_defense',
            'onboarding_protocol',
            'portal_incident',
            'spil_core',
            'stabilize_sandbox',
            'swarm_manager',
            'syntropy_pipeline',
            'system',
            'telemetry_ingest_patch',
            'test_syntropic_weave',
            'timeline_1000y',
            'watcher_simulation',
            'watchers',
            'watchers_voice',
            'year_zero_report'
        ]

        for module_name in system_modules:
            try:
                self._register_system_from_module(module_name)
            except Exception as e:
                logger.warning(f"Failed to register system {module_name}: {e}")

    def _register_system_from_module(self, module_name: str):
        """Register a system from a Python module."""
        try:
            module = importlib.import_module(module_name)
            # Find the main class (usually the first class in the module)
            classes = [obj for name, obj in inspect.getmembers(module)
                      if inspect.isclass(obj) and obj.__module__ == module_name]

            if classes:
                main_class = classes[0]
                system_name = module_name.split('.')[-1]

                system_info = SystemInfo(
                    name=system_name,
                    module=module_name,
                    class_name=main_class.__name__
                )

                # Try to extract capabilities from class docstring or attributes
                if hasattr(main_class, 'capabilities'):
                    system_info.capabilities = main_class.capabilities
                if hasattr(main_class, 'dependencies'):
                    system_info.dependencies = main_class.dependencies

                self.systems[system_name] = system_info
                logger.info(f"Registered system: {system_name}")
            else:
                logger.warning(f"No suitable class found in {module_name}")

        except ImportError:
            logger.debug(f"Module {module_name} not available")

    def initialize_system(self, system_name: str) -> bool:
        """Initialize a specific system."""
        if system_name not in self.systems:
            logger.error(f"System {system_name} not registered")
            return False

        system_info = self.systems[system_name]

        try:
            module = importlib.import_module(system_info.module)
            system_class = getattr(module, system_info.class_name)
            system_info.instance = system_class()
            system_info.status = "initialized"

            # Subscribe to events if the system has event handling
            if hasattr(system_info.instance, 'handle_event'):
                self.event_bus.subscribe(f"{system_name}_event", system_info.instance.handle_event)

            logger.info(f"Initialized system: {system_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize {system_name}: {e}")
            system_info.status = "failed"
            return False

    def start_system(self, system_name: str) -> bool:
        """Start a specific system."""
        if system_name not in self.systems:
            logger.error(f"System {system_name} not registered")
            return False

        system_info = self.systems[system_name]

        if system_info.status != "initialized":
            logger.error(f"System {system_name} not initialized")
            return False

        try:
            if hasattr(system_info.instance, 'start'):
                system_info.instance.start()
            system_info.status = "running"
            logger.info(f"Started system: {system_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to start {system_name}: {e}")
            system_info.status = "failed"
            return False

    def stop_system(self, system_name: str) -> bool:
        """Stop a specific system."""
        if system_name not in self.systems:
            logger.error(f"System {system_name} not registered")
            return False

        system_info = self.systems[system_name]

        try:
            if hasattr(system_info.instance, 'stop'):
                system_info.instance.stop()
            system_info.status = "stopped"
            logger.info(f"Stopped system: {system_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to stop {system_name}: {e}")
            return False

    def initialize_all(self) -> Dict[str, bool]:
        """Initialize all registered systems."""
        results = {}
        for system_name in self.systems:
            results[system_name] = self.initialize_system(system_name)
        return results

    def start_all(self) -> Dict[str, bool]:
        """Start all initialized systems."""
        results = {}
        for system_name in self.systems:
            if self.systems[system_name].status == "initialized":
                results[system_name] = self.start_system(system_name)
            else:
                results[system_name] = False
        return results

    def stop_all(self) -> Dict[str, bool]:
        """Stop all running systems."""
        results = {}
        for system_name in self.systems:
            if self.systems[system_name].status == "running":
                results[system_name] = self.stop_system(system_name)
            else:
                results[system_name] = False
        return results

    def get_system_status(self) -> Dict[str, str]:
        """Get status of all systems."""
        return {name: info.status for name, info in self.systems.items()}

    def get_system_info(self) -> Dict[str, Dict]:
        """Get detailed information about all systems."""
        return {
            name: {
                "status": info.status,
                "capabilities": info.capabilities,
                "dependencies": info.dependencies
            }
            for name, info in self.systems.items()
        }

    def start(self):
        """Start the master orchestrator."""
        logger.info("Starting Master Orchestrator")
        self.event_bus.start()
        self.health_monitor.start()
        self.running = True

        # Initialize and start systems
        init_results = self.initialize_all()
        start_results = self.start_all()

        logger.info(f"Initialization results: {init_results}")
        logger.info(f"Start results: {start_results}")

        # Start main orchestration loop
        self.system_thread = threading.Thread(target=self._orchestration_loop)
        self.system_thread.daemon = True
        self.system_thread.start()

    def stop(self):
        """Stop the master orchestrator."""
        logger.info("Stopping Master Orchestrator")
        self.running = False
        self.stop_all()
        self.health_monitor.stop()
        self.event_bus.stop()
        if self.system_thread:
            self.system_thread.join()

    def _orchestration_loop(self):
        """Main orchestration loop."""
        while self.running:
            try:
                # Publish orchestration heartbeat
                self.event_bus.publish("orchestrator_heartbeat", {
                    "timestamp": time.time(),
                    "systems": self.get_system_status()
                })

                # Check for system health and data flow
                self.health_monitor.check_health()
                self.data_flow_manager.process_data_flow()

                time.sleep(10)  # Orchestration interval

            except Exception as e:
                logger.error(f"Error in orchestration loop: {e}")
                time.sleep(5)

class DataFlowManager:
    """Manages data exchange between systems."""

    def __init__(self, orchestrator: MasterOrchestrator):
        self.orchestrator = orchestrator
        self.data_queues: Dict[str, Queue] = {}

    def register_data_source(self, system_name: str):
        """Register a system as a data source."""
        self.data_queues[system_name] = Queue()

    def send_data(self, from_system: str, to_system: str, data: Any):
        """Send data from one system to another."""
        if to_system in self.data_queues:
            self.data_queues[to_system].put((from_system, data))
            self.orchestrator.event_bus.publish("data_flow", {
                "from": from_system,
                "to": to_system,
                "data_type": type(data).__name__
            })

    def process_data_flow(self):
        """Process pending data flows."""
        for system_name, queue in self.data_queues.items():
            if not queue.empty():
                from_system, data = queue.get()
                system_info = self.orchestrator.systems.get(system_name)
                if system_info and hasattr(system_info.instance, 'receive_data'):
                    try:
                        system_info.instance.receive_data(from_system, data)
                    except Exception as e:
                        logger.error(f"Error processing data for {system_name}: {e}")

class HealthMonitor:
    """Unified health monitoring across all systems."""

    def __init__(self, orchestrator: MasterOrchestrator):
        self.orchestrator = orchestrator
        self.monitoring = False
        self.monitor_thread = None

    def start(self):
        """Start health monitoring."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("Health monitoring started")

    def stop(self):
        """Stop health monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("Health monitoring stopped")

    def check_health(self):
        """Check health of all systems."""
        health_status = {}
        for name, info in self.orchestrator.systems.items():
            try:
                if info.instance and hasattr(info.instance, 'health_check'):
                    health = info.instance.health_check()
                else:
                    health = "unknown"
                health_status[name] = health
            except Exception as e:
                health_status[name] = f"error: {e}"

        self.orchestrator.event_bus.publish("health_status", health_status)

    def _monitor_loop(self):
        """Health monitoring loop."""
        while self.monitoring:
            self.check_health()
            time.sleep(30)  # Health check interval

# Global orchestrator instance
orchestrator = MasterOrchestrator()

if __name__ == "__main__":
    try:
        orchestrator.start()
        logger.info("Master Orchestrator running. Press Ctrl+C to stop.")

        # Keep running until interrupted
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
        orchestrator.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        orchestrator.stop()