"""Entry point for Team Lead agent.

Orchestrator: dialog with user, plans tasks, pushes them to RabbitMQ queues
for workers and reviewers, collects results. Does NOT spawn k8s pods directly
— workers and reviewers are long-lived Deployments that consume from queues.
"""

import sys


def run() -> None:
    """Run the team lead agent: plan tasks, push to queue, collect results."""
    print("[team-lead] agent not yet implemented — exiting", file=sys.stderr)
    raise SystemExit(1)


if __name__ == "__main__":
    run()
