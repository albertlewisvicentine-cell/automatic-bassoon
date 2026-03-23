from abc import ABC, abstractmethod


class Policy(ABC):
    """Abstract base class for all policies."""

    @abstractmethod
    def check(self, state: dict) -> bool:
        """Return True if the policy is satisfied for the given state."""


class AuthPolicy(Policy):
    """Policy that verifies the state contains a valid authenticated identity."""

    def check(self, state: dict) -> bool:
        return bool(state.get("authenticated", False))


class RateLimitPolicy(Policy):
    """Policy that verifies the request count does not exceed the rate limit."""

    def check(self, state: dict) -> bool:
        request_count = state.get("request_count", 0)
        rate_limit = state.get("rate_limit", 100)
        return request_count <= rate_limit


class ALL(Policy):
    """Composite policy that passes only when every sub-policy passes."""

    def __init__(self, *policies: Policy) -> None:
        self.policies = policies

    def check(self, state: dict) -> bool:
        return all(policy.check(state) for policy in self.policies)
