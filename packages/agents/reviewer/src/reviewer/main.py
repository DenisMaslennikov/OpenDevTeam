"""Entry point for Reviewer agent.

Long-lived process: consumes review tasks from RabbitMQ queue (pushed by team
lead), checks results, publishes JSON verdict back to queue, exits after
AGENT_LIFETIME or on idle timeout.
"""

import sys
import time

_IDLE_INTERVAL = 3600


def run() -> None:
    """Run the reviewer agent: consume review tasks from queue, process, repeat."""
    print("[reviewer] agent not yet implemented — idling", file=sys.stderr)
    while True:
        time.sleep(_IDLE_INTERVAL)


if __name__ == "__main__":
    run()
