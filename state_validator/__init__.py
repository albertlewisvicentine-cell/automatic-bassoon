"""state_validator – composable state validation with policies and invariant layers.

Public API
----------
StateValidator   – top-level validator
ALL              – composite policy combinator (all policies must pass)
AuthPolicy       – access-control policy (authentication check)
RateLimitPolicy  – access-control policy (rate-limit check)
LAYER            – factory for invariant layers
checksum_valid   – built-in filesystem check: verifies checksum
size_within_limit – built-in filesystem check: verifies file size
"""

from .checks import checksum_valid, size_within_limit
from .layers import LAYER, Layer
from .policies import ALL, AuthPolicy, Policy, RateLimitPolicy
from .validator import StateValidator

__all__ = [
    "StateValidator",
    "Policy",
    "ALL",
    "AuthPolicy",
    "RateLimitPolicy",
    "LAYER",
    "Layer",
    "checksum_valid",
    "size_within_limit",
]
