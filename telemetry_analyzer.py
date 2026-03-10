import numpy as np
import time
from collections import deque
from scipy.fft import fft, fftfreq

class OneEuroFilter:
    def __init__(self, freq, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        self.freq = freq
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x_prev = None
        self.dx_prev = None

    def _low_pass_filter(self, x, x_prev, alpha):
        return alpha * x + (1 - alpha) * x_prev

    def _alpha(self, cutoff):
        tau = 1.0 / (2 * np.pi * cutoff)
        te = 1.0 / self.freq
        return 1.0 / (1.0 + tau / te)

    def __call__(self, x):
        if self.x_prev is None:
            self.x_prev = x
            self.dx_prev = np.zeros_like(x)
            return x

        # Filter the derivative to get the speed
        dx = (x - self.x_prev) * self.freq
        alpha_d = self._alpha(self.d_cutoff)
        dx_hat = self._low_pass_filter(dx, self.dx_prev, alpha_d)

        # Compute the adaptive cutoff frequency
        cutoff = self.min_cutoff + self.beta * np.abs(dx_hat)
        alpha = self._alpha(cutoff)

        # Filter the signal
        x_hat = self._low_pass_filter(x, self.x_prev, alpha)
        
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        return x_hat

class TelemetryAnalyzer:
    def __init__(self, fps=30, window_size_sec=1.0):
        self.fps = fps
        self.dt = 1.0 / fps
        self.window_size = int(fps * window_size_sec)
        
        # Initialize Filters for tracked points
        # Nose (0), L-Wrist (15), R-Wrist (16), L-Shoulder (11), R-Shoulder (12)
        # Using min_cutoff=1.0 and beta=0.007 for a good balance of jitter vs lag
        self.filters = {
            "nose": OneEuroFilter(fps, min_cutoff=1.0, beta=0.007),
            "l_wrist": OneEuroFilter(fps, min_cutoff=1.0, beta=0.007),
            "r_wrist": OneEuroFilter(fps, min_cutoff=1.0, beta=0.007),
            "l_shoulder": OneEuroFilter(fps, min_cutoff=1.0, beta=0.007),
            "r_shoulder": OneEuroFilter(fps, min_cutoff=1.0, beta=0.007)
        }
        
        self.history = {
            "nose": deque(maxlen=self.window_size),
            "l_wrist": deque(maxlen=self.window_size),
            "r_wrist": deque(maxlen=self.window_size)
        }
        
        self.velocities = deque(maxlen=self.window_size)
        self.accelerations = deque(maxlen=self.window_size)
        
    def _get_dist(self, p1, p2):
        return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    def update(self, landmarks):
        try:
            # 1. Extract raw positions
            raw_ls = np.array([landmarks[11].x, landmarks[11].y])
            raw_rs = np.array([landmarks[12].x, landmarks[12].y])
            raw_nose = np.array([landmarks[0].x, landmarks[0].y])
            raw_lw = np.array([landmarks[15].x, landmarks[15].y])
            raw_rw = np.array([landmarks[16].x, landmarks[16].y])

            # 2. Apply One-Euro Smoothing
            ls = self.filters["l_shoulder"](raw_ls)
            rs = self.filters["r_shoulder"](raw_rs)
            nose = self.filters["nose"](raw_nose)
            lw = self.filters["l_wrist"](raw_lw)
            rw = self.filters["r_wrist"](raw_rw)

            # 3. Body Size Normalization
            shoulder_width = self._get_dist(ls, rs)
            if shoulder_width < 0.01: shoulder_width = 0.1
            
            # 4. Normalize Derivatives
            n_nose = nose / shoulder_width
            n_lw = lw / shoulder_width
            n_rw = rw / shoulder_width
            
            current_pos = (n_lw + n_rw) / 2.0
            
            v = 0
            a = 0
            
            if len(self.history["l_wrist"]) > 0:
                prev_pos = (np.array(self.history["l_wrist"][-1]) + np.array(self.history["r_wrist"][-1])) / 2.0
                v = np.linalg.norm(current_pos - prev_pos) / self.dt
                
                if len(self.velocities) > 0:
                    a = abs(v - self.velocities[-1]) / self.dt
            
            # Update Buffers
            self.history["nose"].append(n_nose)
            self.history["l_wrist"].append(n_lw)
            self.history["r_wrist"].append(n_rw)
            self.velocities.append(v)
            self.accelerations.append(a)
            
            return {"velocity": float(v), "acceleration": float(a)}
        except Exception as e:
            return {"error": str(e)}

    def analyze_frequency(self):
        if len(self.history["l_wrist"]) < 32: return 0, 0
        y_vals = [(p[1]) for p in self.history["l_wrist"]]
        y = np.array(y_vals)
        n = len(y)
        yf = fft(y - np.mean(y))
        xf = fftfreq(n, self.dt)
        mask = (xf > 0.5) & (xf < 8.0)
        if not any(mask): return 0, 0
        idx = np.argmax(np.abs(yf[mask]))
        return float(abs(xf[mask][idx])), float(np.abs(yf[mask][idx]) / n)

    def get_window_stats(self):
        if not self.velocities: return {}
        return {
            "avg_velocity": float(np.mean(self.velocities)),
            "max_acceleration": float(np.max(self.accelerations)),
            "velocity_variance": float(np.var(self.velocities))
        }
