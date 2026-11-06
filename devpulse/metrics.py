from prometheus_client import Counter, Gauge, Histogram

CHECKS_TOTAL = Counter(
    "devpulse_checks_total", "Total HTTP checks executed.", ["target", "status"]
)
CHECK_DURATION = Histogram(
    "devpulse_check_duration_seconds", "HTTP check duration in seconds.", ["target"]
)
TARGET_UP = Gauge("devpulse_target_up", "Latest target availability (1=up, 0=down).", ["target"])
