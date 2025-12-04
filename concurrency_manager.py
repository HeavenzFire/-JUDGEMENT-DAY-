#!/usr/bin/env python3
"""
CONCURRENCY MANAGER
===================

Soft concurrency caps: max 6 concurrent actions per node.
Prevents accidental DoS while preserving felt cadence.
"""

import asyncio
import time
from collections import defaultdict, deque
from typing import Dict, List, Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConcurrencyManager:
    def __init__(self, max_concurrent_per_node: int = 6):
        self.max_concurrent_per_node = max_concurrent_per_node
        self.active_actions: Dict[str, List[asyncio.Task]] = defaultdict(list)
        self.action_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))

        # Rate limiting
        self.node_rates: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.rate_window_seconds = 60  # 1 minute window
        self.max_actions_per_minute = 10

        # Action types and their priorities
        self.action_priorities = {
            'recitation': 1,
            'attestation': 2,
            'sealing': 3,
            'onboarding': 4,
            'broadcast': 5,
            'sync': 6,
            'maintenance': 7
        }

    async def submit_action(self, node_id: str, action_type: str,
                          action_func: Callable, *args, **kwargs) -> Optional[Any]:
        """Submit an action for execution with concurrency control"""

        # Check rate limits
        if not self.check_rate_limit(node_id):
            logger.warning("Rate limit exceeded for node %s", node_id)
            raise asyncio.QueueFull("Rate limit exceeded")

        # Check concurrency limits
        if len(self.active_actions[node_id]) >= self.max_concurrent_per_node:
            logger.warning("Concurrency limit reached for node %s", node_id)
            raise asyncio.QueueFull("Concurrency limit reached")

        # Create task
        task = asyncio.create_task(self._execute_action(node_id, action_type, action_func, *args, **kwargs))
        self.active_actions[node_id].append(task)

        # Record action
        self.record_action(node_id, action_type)

        try:
            result = await task
            return result
        finally:
            # Remove completed task
            if task in self.active_actions[node_id]:
                self.active_actions[node_id].remove(task)

    async def _execute_action(self, node_id: str, action_type: str,
                            action_func: Callable, *args, **kwargs) -> Any:
        """Execute action with error handling"""
        try:
            logger.info("Executing %s action for node %s", action_type, node_id)
            start_time = time.time()

            result = await action_func(*args, **kwargs)

            duration = time.time() - start_time
            logger.info("Completed %s action for node %s in %.2fs",
                       action_type, node_id, duration)

            return result

        except Exception as e:
            logger.error("Action %s failed for node %s: %s", action_type, node_id, e)
            raise

    def check_rate_limit(self, node_id: str) -> bool:
        """Check if node is within rate limits"""
        now = time.time()
        node_actions = self.node_rates[node_id]

        # Remove old actions outside the window
        while node_actions and (now - node_actions[0]) > self.rate_window_seconds:
            node_actions.popleft()

        # Check if under limit
        return len(node_actions) < self.max_actions_per_minute

    def record_action(self, node_id: str, action_type: str):
        """Record action for rate limiting and history"""
        now = time.time()
        self.node_rates[node_id].append(now)

        # Record in history
        self.action_history[node_id].append({
            'timestamp': now,
            'action_type': action_type,
            'priority': self.action_priorities.get(action_type, 0)
        })

    def get_node_stats(self, node_id: str) -> Dict:
        """Get statistics for a node"""
        active_count = len(self.active_actions[node_id])
        recent_actions = list(self.action_history[node_id])

        # Calculate actions per minute
        now = time.time()
        recent_minute = [a for a in recent_actions if (now - a['timestamp']) <= 60]
        actions_per_minute = len(recent_minute)

        return {
            'active_actions': active_count,
            'actions_per_minute': actions_per_minute,
            'total_actions': len(recent_actions),
            'concurrency_limit': self.max_concurrent_per_node,
            'rate_limit': self.max_actions_per_minute
        }

    def get_global_stats(self) -> Dict:
        """Get global concurrency statistics"""
        total_active = sum(len(actions) for actions in self.active_actions.values())
        total_nodes = len(self.active_actions)

        return {
            'total_active_actions': total_active,
            'active_nodes': total_nodes,
            'max_concurrent_per_node': self.max_concurrent_per_node,
            'rate_limit_per_minute': self.max_actions_per_minute
        }

    async def wait_for_slot(self, node_id: str) -> None:
        """Wait for an available concurrency slot"""
        while len(self.active_actions[node_id]) >= self.max_concurrent_per_node:
            await asyncio.sleep(1)

    def cancel_node_actions(self, node_id: str, action_type: Optional[str] = None):
        """Cancel actions for a node, optionally filtering by type"""
        tasks_to_cancel = []

        for task in self.active_actions[node_id]:
            if action_type is None or task.get_name() == action_type:
                task.cancel()
                tasks_to_cancel.append(task)

        for task in tasks_to_cancel:
            self.active_actions[node_id].remove(task)

        logger.info("Cancelled %d actions for node %s", len(tasks_to_cancel), node_id)

    async def graceful_shutdown(self, timeout: float = 30.0):
        """Gracefully shutdown all active actions"""
        logger.info("Initiating graceful shutdown...")

        # Cancel all active tasks
        all_tasks = []
        for node_tasks in self.active_actions.values():
            all_tasks.extend(node_tasks)

        for task in all_tasks:
            task.cancel()

        # Wait for completion or timeout
        try:
            await asyncio.wait(all_tasks, timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning("Shutdown timed out, forcing cancellation")

        logger.info("Shutdown complete")

# Global instance
concurrency_manager = ConcurrencyManager()

async def submit_swarm_action(node_id: str, action_type: str,
                            action_func: Callable, *args, **kwargs) -> Optional[Any]:
    """Global function to submit swarm actions"""
    return await concurrency_manager.submit_action(node_id, action_type, action_func, *args, **kwargs)

def get_concurrency_stats() -> Dict:
    """Get global concurrency statistics"""
    return concurrency_manager.get_global_stats()

def get_node_concurrency_stats(node_id: str) -> Dict:
    """Get concurrency statistics for a specific node"""
    return concurrency_manager.get_node_stats(node_id)