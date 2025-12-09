# fft_anomaly_detector.py
# Dependencies: numpy, requests
# pip install numpy requests

import time
import threading
import collections
import numpy as np
import requests

class NodeRingBuffer:
    def __init__(self, length=256):
        self.buf = collections.deque(maxlen=length)

    def push(self, value):
        self.buf.append(value)

    def is_full(self):
        return len(self.buf) == self.buf.maxlen

    def as_array(self):
        return np.array(self.buf, dtype=float)

class FFTAnomalyDetector:
    def __init__(self, telemetry_client, webhook_url=None, sr=50, window=256):
        """
        telemetry_client: callable to get latest node list / metrics, or a reference to the telemetry.metrics dict
        webhook_url: where to send alerts
        sr: sampling rate (Hz) expected from node feed
        window: FFT window size
        """
        self.telemetry_client = telemetry_client
        self.webhook_url = webhook_url
        self.sr = sr
        self.window = window
        self.buffers = {}  # node_id -> NodeRingBuffer
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._run_loop, daemon=True)
        self._t.start()

    def ingest_point(self, node_id, coherence_value):
        b = self.buffers.get(node_id)
        if b is None:
            b = NodeRingBuffer(length=self.window)
            self.buffers[node_id] = b
        b.push(coherence_value)

    def _analyze_buffer(self, arr):
        # arr: numpy array of coherence amplitudes
        # Simple FFT magnitude and peak detection
        yf = np.fft.rfft(arr * np.hanning(len(arr)))
        xf = np.fft.rfftfreq(len(arr), 1.0 / self.sr)
        mag = np.abs(yf)
        # dominant freq
        peak_idx = mag.argmax()
        peak_freq = xf[peak_idx]
        peak_mag = mag[peak_idx]
        return peak_freq, peak_mag, xf, mag

    def _should_alert(self, node_id, peak_freq, peak_mag):
        # Expected band ~ 7.0 - 8.5 Hz (configurable). Alert if peak is outside or energy high in harmonics.
        if peak_freq < 6.0 or peak_freq > 10.0:
            return True
        # If peak magnitude is abnormally large compared to median magnitudes, alert
        # (simple heuristic)
        return False

    def _alert(self, payload):
        print("[FFT ALERT]", payload)
        if self.webhook_url:
            try:
                requests.post(self.webhook_url, json=payload, timeout=1.0)
            except Exception as e:
                print("[WebhookError]", e)

    def _run_loop(self):
        while not self._stop.is_set():
            # snapshot telemetry source
            metrics = self.telemetry_client()  # expected: dict node_id -> metric dict
            if not metrics:
                time.sleep(0.5)
                continue
            # ingest recent coherence values
            for nid, m in metrics.items():
                self.ingest_point(nid, m.get("coherence", 0.0))
            # analyze full buffers occasionally
            for nid, buf in list(self.buffers.items()):
                if buf.is_full():
                    arr = buf.as_array()
                    peak_freq, peak_mag, xf, mag = self._analyze_buffer(arr)
                    if self._should_alert(nid, peak_freq, peak_mag):
                        payload = {
                            "node_id": nid,
                            "peak_frequency": float(peak_freq),
                            "peak_magnitude": float(peak_mag),
                            "timestamp": time.time()
                        }
                        self._alert(payload)
                        # optional: clear buffer after alert to avoid spamming
                        buf.buf.clear()
            time.sleep(1.0)

    def stop(self):
        self._stop.set()
        self._t.join(timeout=2.0)

# Example wiring when running inside telemetry_server:
# from fft_anomaly_detector import FFTAnomalyDetector
# detector = FFTAnomalyDetector(lambda: telemetry.metrics.copy(), webhook_url="https://hooks.example/telemetry")