#!/usr/bin/env python3
# dragon_gossip_v2_1_final.py — Continuous Consensus Module v2.1
# Refined for non-blocking operation and robustness

import time
import math
import logging
from collections import deque
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - CONSENSUS - %(message)s')

class ContinuousConsensusModule:
    def __init__(self, quorum_window: float = 2.0, min_quorum: int = 1, ema_alpha: float = 0.15, outlier_threshold: float = 0.20, recency_half_life: float = 1.0, history_len: int = 50):
        self.quorum_window = quorum_window
        self.min_quorum = max(1, min_quorum)
        self.ema_alpha = ema_alpha
        self.outlier_delta = outlier_threshold
        self.recency_half_life = max(0.001, recency_half_life)
        self.consensus_weight = 1.0
        self.global_syntropy = 0.0
        self.last_update = None
        self._history = deque(maxlen=history_len)
        self.running = False
        self._thread = None

    def _recency_weight(self, age: float) -> float:
        return 0.5 ** (age / self.recency_half_life)

    def _huber_dampen(self, residual: float) -> float:
        d = self.outlier_delta
        return residual if abs(residual) <= d else d * math.copysign(1, residual)

    def update_once(self, peers: dict, local_state: dict):
        now = time.time()
        self.last_update = now
        samples = []

        local_safety = local_state.get("safety", "RED")
        if local_safety == "GREEN":
            samples.append({"id": local_state.get("id", "self"), "syntropy": float(local_state.get("syntropy", 0.0)), "age": 0.0, "recency_w": 1.0, "safety": local_safety})

        for pid, d in peers.items():
            try:
                last_seen = float(d.get("last_seen", 0.0))
            except (TypeError, ValueError):
                continue
            age = max(0.0, now - last_seen)
            if age > self.quorum_window or d.get("safety") != "GREEN":
                continue
            try:
                syn = float(d.get("syntropy", 0.0))
            except (TypeError, ValueError):
                continue
            rec_w = self._recency_weight(age)
            samples.append({"id": pid, "syntropy": syn, "age": age, "recency_w": rec_w, "safety": d.get("safety")})

        if len(samples) < self.min_quorum:
            # Fallback to local if not enough samples
            self.global_syntropy = float(local_state.get("syntropy", 0.0))
            self.consensus_weight = 0.3
            self._push_history(self.global_syntropy)
            logging.debug("Consensus: insufficient samples, fallback to local")
            return

        weighted_sum = sum(s["syntropy"] * s.get("recency_w",1.0) for s in samples)
        total_w = sum(s.get("recency_w",1.0) for s in samples)
        mean = weighted_sum / max(1e-9, total_w)

        refined = sum((mean + self._huber_dampen(s["syntropy"] - mean)) * s.get("recency_w",1.0) for s in samples) / max(1e-9, total_w)

        count_factor = min(1.0, len(samples)/max(1.0,len(peers)+1))
        rec_weights = sorted([s.get("recency_w",0.0) for s in samples])
        median_rec = rec_weights[len(rec_weights)//2] if rec_weights else 0.0
        green_frac = sum(1 for s in samples if s.get("safety")=="GREEN") / max(1.0,len(samples))
        reliability = count_factor * median_rec * green_frac
        self.consensus_weight = 0.2 + 0.8*(reliability**0.75)

        prev = self._history[-1] if self._history else refined
        adaptive_alpha = self.ema_alpha * (0.5 + 0.5*abs(refined-prev))
        self.global_syntropy = max(0.0, min(1.0, prev + adaptive_alpha*(refined-prev)))
        self._push_history(self.global_syntropy)

    def _push_history(self, value: float):
        self._history.append(value)

    def get_weighted_syntropy(self, local_state: dict) -> float:
        local_syn = float(local_state.get("syntropy",0.0))
        return max(0.0,min(1.0, local_syn*(1.0-self.consensus_weight)+self.global_syntropy*self.consensus_weight))

    def snapshot(self) -> dict:
        return {"last_update":self.last_update, "consensus_weight":self.consensus_weight, "global_syntropy":self.global_syntropy, "history_len":len(self._history)}

    def _continuous_loop(self, get_peer_state, get_local_state, cycle_delay):
        while self.running:
            try:
                peers = get_peer_state()
                local = get_local_state()
                self.update_once(peers, local)
            except Exception:
                logging.exception("Error in consensus loop")
            finally:
                time.sleep(cycle_delay)

    def run_continuous(self, get_peer_state, get_local_state, cycle_delay=0.25, threaded=True):
        if self.running:
            return  # already running
        self.running = True
        if threaded:
            self._thread = threading.Thread(target=self._continuous_loop, args=(get_peer_state,get_local_state,cycle_delay), daemon=True)
            self._thread.start()
        else:
            self._continuous_loop(get_peer_state,get_local_state,cycle_delay)

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join()
            self._thread = None