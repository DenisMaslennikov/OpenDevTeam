"""Entry point for Worker agent.

Long-lived process: consumes tasks from RabbitMQ queue (pushed by team lead),
runs in WORKER_MODE (researcher or coder), exits after AGENT_LIFETIME or on
idle timeout.
"""

import sys
import time

_IDLE_INTERVAL = 3600


def run() -> None:
    """Run the worker agent: consume tasks from queue, process, repeat."""
    print("[worker] agent not yet implemented — idling", file=sys.stderr)
    while True:
        time.sleep(_IDLE_INTERVAL)


if __name__ == "__main__":
    run()
