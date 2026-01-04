"""
Holographic Projections Module for GuardianOS v2.5.0
LED array displays for visual comfort patterns
"""

import time
import math
import numpy as np
from typing import List, Tuple, Optional
import threading

class HolographicComfortSystem:
    def __init__(self, led_matrix_width: int = 32, led_matrix_height: int = 32):
        self.width = led_matrix_width
        self.height = led_matrix_height
        self.is_active = False
        self.current_pattern = None
        self.animation_thread: Optional[threading.Thread] = None
        self.stop_animation = False

        # Color definitions (RGB tuples)
        self.colors = {
            'white': (255, 255, 255),
            'soft_blue': (100, 150, 255),
            'gentle_green': (100, 255, 150),
            'warm_orange': (255, 180, 100),
            'calm_purple': (150, 100, 255),
            'peaceful_pink': (255, 150, 200)
        }

        # Pre-defined comfort patterns
        self.patterns = {
            'breathing_circle': self._breathing_circle,
            'flowing_waves': self._flowing_waves,
            'gentle_pulse': self._gentle_pulse,
            'starfield': self._starfield,
            'mandala': self._mandala,
            'heartbeat': self._heartbeat
        }

    def initialize_display(self) -> bool:
        """Initialize LED matrix display"""
        try:
            # Placeholder for LED matrix initialization
            # In production: initialize LED matrix library (e.g., rpi_ws281x)
            print("Holographic display initialized.")
            return True
        except Exception as e:
            print(f"Failed to initialize holographic display: {e}")
            return False

    def start_pattern(self, pattern_name: str, duration: Optional[float] = None):
        """Start displaying a comfort pattern"""
        if pattern_name not in self.patterns:
            print(f"Unknown pattern: {pattern_name}")
            return

        self.stop_current_pattern()
        self.current_pattern = pattern_name
        self.is_active = True
        self.stop_animation = False

        self.animation_thread = threading.Thread(
            target=self._animate_pattern,
            args=(pattern_name, duration)
        )
        self.animation_thread.daemon = True
        self.animation_thread.start()

    def stop_current_pattern(self):
        """Stop the currently playing pattern"""
        self.stop_animation = True
        self.is_active = False
        if self.animation_thread and self.animation_thread.is_alive():
            self.animation_thread.join(timeout=2.0)
        self.clear_display()

    def _animate_pattern(self, pattern_name: str, duration: Optional[float]):
        """Animate the specified pattern"""
        start_time = time.time()
        frame_count = 0

        while not self.stop_animation:
            try:
                # Check duration limit
                if duration and time.time() - start_time > duration:
                    break

                # Generate frame
                frame = self.patterns[pattern_name](frame_count)

                # Display frame
                self._display_frame(frame)

                # Frame rate control (30 FPS)
                time.sleep(1/30)
                frame_count += 1

            except Exception as e:
                print(f"Animation error: {e}")
                break

        self.is_active = False

    def _breathing_circle(self, frame: int) -> np.ndarray:
        """Generate breathing circle pattern"""
        # Create empty frame
        frame_data = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Calculate breathing effect
        breath_cycle = (frame % 180) / 180.0  # 3-second cycle
        radius = int(8 + 6 * (0.5 + 0.5 * math.sin(2 * math.pi * breath_cycle)))

        # Draw expanding/contracting circle
        center_x, center_y = self.width // 2, self.height // 2

        for y in range(self.height):
            for x in range(self.width):
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                if distance <= radius:
                    # Soft blue gradient
                    intensity = max(0, 1 - (distance / radius))
                    frame_data[y, x] = (
                        int(100 * intensity),
                        int(150 * intensity),
                        int(255 * intensity)
                    )

        return frame_data

    def _flowing_waves(self, frame: int) -> np.ndarray:
        """Generate flowing waves pattern"""
        frame_data = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        for y in range(self.height):
            for x in range(self.width):
                # Create wave effect
                wave1 = math.sin((x + frame) * 0.1) * math.sin((y + frame * 0.5) * 0.1)
                wave2 = math.sin((x - frame) * 0.15) * math.cos((y + frame * 0.3) * 0.15)

                combined_wave = (wave1 + wave2) * 0.5
                intensity = max(0, min(1, (combined_wave + 1) * 0.5))

                # Gentle green-blue gradient
                frame_data[y, x] = (
                    int(50 * intensity),
                    int(200 * intensity),
                    int(150 * intensity)
                )

        return frame_data

    def _gentle_pulse(self, frame: int) -> np.ndarray:
        """Generate gentle pulsing pattern"""
        frame_data = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Slow pulse effect
        pulse = (math.sin(frame * 0.05) + 1) * 0.5
        intensity = 0.3 + 0.7 * pulse

        # Fill entire display with soft pulsing color
        color = self.colors['warm_orange']
        for y in range(self.height):
            for x in range(self.width):
                frame_data[y, x] = (
                    int(color[0] * intensity),
                    int(color[1] * intensity),
                    int(color[2] * intensity)
                )

        return frame_data

    def _starfield(self, frame: int) -> np.ndarray:
        """Generate calming starfield pattern"""
        frame_data = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Generate pseudo-random stars
        np.random.seed(42)  # Consistent pattern

        for i in range(20):  # 20 stars
            x = int((i * 37 + frame * 2) % self.width)
            y = int((i * 23 + frame) % self.height)

            # Twinkling effect
            twinkle = (math.sin(frame * 0.1 + i) + 1) * 0.5
            brightness = int(255 * twinkle)

            if 0 <= x < self.width and 0 <= y < self.height:
                frame_data[y, x] = (brightness, brightness, brightness)

        return frame_data

    def _mandala(self, frame: int) -> np.ndarray:
        """Generate mandala pattern for meditation"""
        frame_data = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        center_x, center_y = self.width // 2, self.height // 2

        for y in range(self.height):
            for x in range(self.width):
                # Calculate polar coordinates
                dx, dy = x - center_x, y - center_y
                distance = math.sqrt(dx**2 + dy**2)
                angle = math.atan2(dy, dx)

                # Create mandala pattern
                rings = int(distance / 3)
                petals = int((angle + frame * 0.02) / (math.pi / 6)) % 12

                # Color based on ring and petal
                if rings % 2 == petals % 2:
                    color = self.colors['calm_purple']
                    intensity = 0.8
                else:
                    color = self.colors['peaceful_pink']
                    intensity = 0.6

                frame_data[y, x] = (
                    int(color[0] * intensity),
                    int(color[1] * intensity),
                    int(color[2] * intensity)
                )

        return frame_data

    def _heartbeat(self, frame: int) -> np.ndarray:
        """Generate heartbeat visualization"""
        frame_data = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Heartbeat pattern (approximate 72 BPM)
        beat_cycle = frame % 90  # 3-second cycle at 30 FPS

        if beat_cycle < 5:  # Systole spike
            intensity = 1.0
        elif beat_cycle < 15:  # Quick drop
            intensity = 0.3
        elif beat_cycle < 25:  # Small bump (T wave)
            intensity = 0.6
        else:  # Resting state
            intensity = 0.2

        # Draw heartbeat line across center
        center_y = self.height // 2
        for x in range(self.width):
            # Create ECG-like waveform
            wave_pos = center_y + int(10 * math.sin(x * 0.2) * intensity)
            if 0 <= wave_pos < self.height:
                frame_data[wave_pos, x] = (
                    int(255 * intensity),
                    int(100 * intensity),
                    int(100 * intensity)
                )

        return frame_data

    def _display_frame(self, frame: np.ndarray):
        """Display frame on LED matrix"""
        # Placeholder for actual LED matrix display
        # In production: send frame data to LED matrix hardware
        pass

    def clear_display(self):
        """Clear the display"""
        frame_data = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self._display_frame(frame_data)

    def get_available_patterns(self) -> List[str]:
        """Return list of available patterns"""
        return list(self.patterns.keys())