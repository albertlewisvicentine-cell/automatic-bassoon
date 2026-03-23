from typing import List, Optional

from .layers import Layer
from .policies import Policy


class StateValidator:
    """Validates a state dict against an access-control policy and a set of
    invariant layers.

    Parameters
    ----------
    policy:
        A :class:`~state_validator.policies.Policy` instance (or composite
        such as :class:`~state_validator.policies.ALL`) that governs
        access-control checks.  When *None* the access-control check is
        skipped.
    invariant_layers:
        A list of :class:`~state_validator.layers.Layer` objects that encode
        domain-level invariants (e.g. filesystem integrity).  When the list
        is empty all invariant checks are considered satisfied.

    Example
    -------
    ::

        validator = StateValidator(
            policy=ALL(
                AuthPolicy(),
                RateLimitPolicy()
            ),
            invariant_layers=[
                LAYER("filesystem",
                    checksum_valid,
                    size_within_limit
                )
            ]
        )

        state = {
            "authenticated": True,
            "request_count": 5,
            "rate_limit": 100,
            "checksum": "abc123",
            "expected_checksum": "abc123",
            "size": 512,
        }
        assert validator.validate(state)
    """

    def __init__(
        self,
        policy: Optional[Policy] = None,
        invariant_layers: Optional[List[Layer]] = None,
    ) -> None:
        self.policy = policy
        self.invariant_layers: List[Layer] = invariant_layers or []

    def validate(self, state: dict) -> bool:
        """Return True when the state satisfies the policy and all invariant layers."""
        if self.policy is not None and not self.policy.check(state):
            return False
        return all(layer.validate(state) for layer in self.invariant_layers)
