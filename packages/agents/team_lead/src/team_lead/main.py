"""Entry point for Team Lead agent.

Orchestrator: dialog with user, plans tasks, pushes them to RabbitMQ queues
for workers and reviewers, collects results. Does NOT spawn k8s pods directly
— workers and reviewers are long-lived Deployments that consume from queues.
"""

import sys
import time

_IDLE_INTERVAL = 3600


def run() -> None:
    """Run the team lead agent: plan tasks, push to queue, collect results."""
    print("[team-lead] agent not yet implemented — idling", file=sys.stderr)
    while True:
        time.sleep(_IDLE_INTERVAL)


if __name__ == "__main__":
    run()
