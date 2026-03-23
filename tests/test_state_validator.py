"""Tests for the state_validator package."""
import hashlib

import pytest

from state_validator import (
    ALL,
    LAYER,
    AuthPolicy,
    RateLimitPolicy,
    StateValidator,
    checksum_valid,
    size_within_limit,
)


# ---------------------------------------------------------------------------
# AuthPolicy
# ---------------------------------------------------------------------------

class TestAuthPolicy:
    def test_passes_when_authenticated(self):
        assert AuthPolicy().check({"authenticated": True}) is True

    def test_fails_when_not_authenticated(self):
        assert AuthPolicy().check({"authenticated": False}) is False

    def test_fails_when_key_missing(self):
        assert AuthPolicy().check({}) is False


# ---------------------------------------------------------------------------
# RateLimitPolicy
# ---------------------------------------------------------------------------

class TestRateLimitPolicy:
    def test_passes_when_under_limit(self):
        state = {"request_count": 50, "rate_limit": 100}
        assert RateLimitPolicy().check(state) is True

    def test_passes_when_at_limit(self):
        state = {"request_count": 100, "rate_limit": 100}
        assert RateLimitPolicy().check(state) is True

    def test_fails_when_over_limit(self):
        state = {"request_count": 101, "rate_limit": 100}
        assert RateLimitPolicy().check(state) is False

    def test_default_limit_is_100(self):
        assert RateLimitPolicy().check({"request_count": 100}) is True
        assert RateLimitPolicy().check({"request_count": 101}) is False

    def test_default_count_is_0(self):
        assert RateLimitPolicy().check({}) is True


# ---------------------------------------------------------------------------
# ALL combinator
# ---------------------------------------------------------------------------

class TestALL:
    def test_passes_when_all_policies_pass(self):
        state = {"authenticated": True, "request_count": 5, "rate_limit": 100}
        assert ALL(AuthPolicy(), RateLimitPolicy()).check(state) is True

    def test_fails_when_auth_fails(self):
        state = {"authenticated": False, "request_count": 5, "rate_limit": 100}
        assert ALL(AuthPolicy(), RateLimitPolicy()).check(state) is False

    def test_fails_when_rate_limit_exceeded(self):
        state = {"authenticated": True, "request_count": 200, "rate_limit": 100}
        assert ALL(AuthPolicy(), RateLimitPolicy()).check(state) is False

    def test_fails_when_both_fail(self):
        state = {"authenticated": False, "request_count": 200, "rate_limit": 100}
        assert ALL(AuthPolicy(), RateLimitPolicy()).check(state) is False

    def test_passes_with_no_policies(self):
        assert ALL().check({}) is True


# ---------------------------------------------------------------------------
# checksum_valid
# ---------------------------------------------------------------------------

class TestChecksumValid:
    def test_passes_with_matching_direct_checksums(self):
        state = {"checksum": "abc123", "expected_checksum": "abc123"}
        assert checksum_valid(state) is True

    def test_fails_with_mismatched_direct_checksums(self):
        state = {"checksum": "abc123", "expected_checksum": "xyz789"}
        assert checksum_valid(state) is False

    def test_passes_with_content_matching_sha256(self):
        content = b"hello world"
        expected = hashlib.sha256(content).hexdigest()
        state = {"content": content, "expected_checksum": expected}
        assert checksum_valid(state) is True

    def test_passes_with_str_content_matching_sha256(self):
        content = "hello world"
        expected = hashlib.sha256(content.encode()).hexdigest()
        state = {"content": content, "expected_checksum": expected}
        assert checksum_valid(state) is True

    def test_fails_with_content_not_matching_sha256(self):
        state = {"content": b"hello", "expected_checksum": "bad_checksum"}
        assert checksum_valid(state) is False

    def test_passes_when_no_expected_checksum(self):
        assert checksum_valid({}) is True
        assert checksum_valid({"checksum": "abc"}) is True

    def test_fails_when_expected_checksum_present_but_no_data(self):
        assert checksum_valid({"expected_checksum": "abc123"}) is False


# ---------------------------------------------------------------------------
# size_within_limit
# ---------------------------------------------------------------------------

class TestSizeWithinLimit:
    def test_passes_when_size_is_zero(self):
        assert size_within_limit({"size": 0}) is True

    def test_passes_when_size_is_under_limit(self):
        assert size_within_limit({"size": 512, "size_limit": 1024}) is True

    def test_passes_when_size_equals_limit(self):
        assert size_within_limit({"size": 1024, "size_limit": 1024}) is True

    def test_fails_when_size_exceeds_limit(self):
        assert size_within_limit({"size": 1025, "size_limit": 1024}) is False

    def test_default_limit_is_1_mib(self):
        assert size_within_limit({"size": 1024 * 1024}) is True
        assert size_within_limit({"size": 1024 * 1024 + 1}) is False

    def test_default_size_is_0(self):
        assert size_within_limit({}) is True


# ---------------------------------------------------------------------------
# LAYER factory
# ---------------------------------------------------------------------------

class TestLAYER:
    def test_layer_name_is_stored(self):
        layer = LAYER("filesystem", checksum_valid, size_within_limit)
        assert layer.name == "filesystem"

    def test_layer_checks_are_stored(self):
        layer = LAYER("filesystem", checksum_valid, size_within_limit)
        assert checksum_valid in layer.checks
        assert size_within_limit in layer.checks

    def test_layer_validate_passes_when_all_checks_pass(self):
        layer = LAYER("filesystem", checksum_valid, size_within_limit)
        state = {
            "checksum": "abc",
            "expected_checksum": "abc",
            "size": 100,
            "size_limit": 1024,
        }
        assert layer.validate(state) is True

    def test_layer_validate_fails_when_checksum_check_fails(self):
        layer = LAYER("filesystem", checksum_valid, size_within_limit)
        state = {"checksum": "abc", "expected_checksum": "xyz", "size": 100}
        assert layer.validate(state) is False

    def test_layer_validate_fails_when_size_check_fails(self):
        layer = LAYER("filesystem", checksum_valid, size_within_limit)
        state = {
            "checksum": "abc",
            "expected_checksum": "abc",
            "size": 9999,
            "size_limit": 100,
        }
        assert layer.validate(state) is False


# ---------------------------------------------------------------------------
# StateValidator – the complete integration scenario from the problem statement
# ---------------------------------------------------------------------------

class TestStateValidator:
    def _make_validator(self):
        return StateValidator(
            policy=ALL(
                AuthPolicy(),
                RateLimitPolicy(),
            ),
            invariant_layers=[
                LAYER("filesystem", checksum_valid, size_within_limit)
            ],
        )

    def _good_state(self):
        return {
            "authenticated": True,
            "request_count": 5,
            "rate_limit": 100,
            "checksum": "abc123",
            "expected_checksum": "abc123",
            "size": 512,
            "size_limit": 1024 * 1024,
        }

    def test_valid_state_passes(self):
        assert self._make_validator().validate(self._good_state()) is True

    def test_fails_when_not_authenticated(self):
        state = {**self._good_state(), "authenticated": False}
        assert self._make_validator().validate(state) is False

    def test_fails_when_rate_limit_exceeded(self):
        state = {**self._good_state(), "request_count": 101, "rate_limit": 100}
        assert self._make_validator().validate(state) is False

    def test_fails_when_checksum_invalid(self):
        state = {**self._good_state(), "checksum": "wrong"}
        assert self._make_validator().validate(state) is False

    def test_fails_when_size_exceeds_limit(self):
        state = {**self._good_state(), "size": 2 * 1024 * 1024}
        assert self._make_validator().validate(state) is False

    def test_no_policy_skips_policy_check(self):
        validator = StateValidator(
            invariant_layers=[LAYER("filesystem", checksum_valid, size_within_limit)]
        )
        state = {
            "checksum": "ok",
            "expected_checksum": "ok",
            "size": 10,
        }
        assert validator.validate(state) is True

    def test_no_invariant_layers_skips_layer_check(self):
        validator = StateValidator(
            policy=ALL(AuthPolicy(), RateLimitPolicy())
        )
        state = {"authenticated": True, "request_count": 0}
        assert validator.validate(state) is True

    def test_empty_validator_always_passes(self):
        assert StateValidator().validate({}) is True
        assert StateValidator().validate({"authenticated": False}) is True
