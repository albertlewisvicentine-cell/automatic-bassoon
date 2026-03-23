class CompositePolicy:
    """A policy that composes multiple policies, supporting arbitrary nesting.

    All policies in the list must pass for the composite policy to pass.
    A ``CompositePolicy`` may contain other ``CompositePolicy`` instances,
    enabling deeply nested policy structures.

    Each item in *policies* must implement ``evaluate(context) -> bool``.

    Evaluation short-circuits: as soon as one policy returns ``False`` the
    remaining policies in that composite (and any outer composite) are not
    evaluated.

    Example::

        policy = CompositePolicy([
            CompositePolicy([
                CompositePolicy([
                    leaf_policy_a,
                    leaf_policy_b,
                ]),
                leaf_policy_c,
            ]),
            leaf_policy_d,
        ])
        result = policy.evaluate(context)
    """

    def __init__(self, policies):
        if not isinstance(policies, list):
            raise TypeError("policies must be a list")
        for i, policy in enumerate(policies):
            if not callable(getattr(policy, "evaluate", None)):
                raise TypeError(
                    f"policies[{i}] must implement an evaluate(context) method"
                )
        self.policies = policies

    def evaluate(self, context):
        """Evaluate all policies against *context*.

        Returns ``True`` when every policy passes, ``False`` otherwise.
        Evaluation short-circuits on the first failing policy.
        Nested ``CompositePolicy`` instances are evaluated recursively.
        """
        for policy in self.policies:
            if not policy.evaluate(context):
                return False
        return True
