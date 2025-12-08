# telemetry_ingest_patch.py
# Lightweight batch poster for telemetry_server ingest API
# sync-friendly (uses requests). For async loops, see note below.

import time
import requests
import threading
import queue
from typing import List, Dict

class Ingestor:
    def __init__(self, endpoint="http://localhost:9100/ingest", batch_interval: float = 0.5, batch_size: int = 200):
        """
        endpoint: telemetry ingest endpoint
        batch_interval: seconds between posts
        batch_size: max nodes per batch
        """
        self.endpoint = endpoint
        self.batch_interval = batch_interval
        self.batch_size = batch_size
        self._q = queue.Queue()
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._poster_loop, daemon=True)
        self._t.start()

    def enqueue_nodes(self, nodes: List[Dict]):
        """
        nodes: list of node dicts:
          {"node_id": "n_x_y", "coherence": 0.99, "drift": 0.0004, "impedance": 12.4, "timestamp": 1234567.0}
        """
        for n in nodes:
            self._q.put(n)

    def _poster_loop(self):
        import json
        import requests
        while not self._stop.is_set():
            batch = []
            start = time.time()
            # collect up to batch_size (non-blocking)
            while len(batch) < self.batch_size:
                try:
                    n = self._q.get(timeout=0.01)
                    batch.append(n)
                except Exception:
                    break
            if not batch:
                # nothing to send; sleep until next interval
                time.sleep(self.batch_interval)
                continue

            # POST batches individually (server expects one node per POST in current telemetry_server.py)
            # To reduce overhead, attempt a multi-node batch endpoint if telemetry_server supports it.
            # For now we POST sequentially but non-blocking to avoid blocking the simulation loop.
            for node in batch:
                try:
                    resp = requests.post(self.endpoint, json=node, timeout=0.4)
                    # optional: check resp.status_code
                except Exception as e:
                    # best-effort: silence to avoid crashing simulation; optionally buffer for retry
                    print(f"[TelemetryPostError] {e}")
            # wait to the next scheduled post
            elapsed = time.time() - start
            if elapsed < self.batch_interval:
                time.sleep(self.batch_interval - elapsed)

    def stop(self):
        self._stop.set()
        self._t.join(timeout=1.0)

# -------------------------
# Example integration snippet to use in your simulation tick loop:
# from telemetry_ingest_patch import Ingestor
# ing = Ingestor(endpoint="http://127.0.0.1:9100/ingest", batch_interval=0.25, batch_size=256)
#
# def simulation_tick_and_report():
#     # return list of node metrics for this tick
#     nodes = []
#     for n in toroidal_grid.nodes:
#         nodes.append({
#             "node_id": f"n_{n.x}_{n.y}",
#             "coherence": compute_coherence_for_node(n),
#             "drift": compute_drift_for_node(n),
#             "impedance": compute_impedance_for_node(n),
#             "timestamp": time.time()
#         })
#     # enqueue in background
#     ing.enqueue_nodes(nodes)
#
# # When shutting down:
# ing.stop()
#
# NOTE: If your simulation loop is async (asyncio), implement an aiohttp-based batcher instead.