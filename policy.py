class CompositePolicy:
    """A policy that composes multiple policies together (all must pass)."""

    def __init__(self, policies):
        self.policies = policies

    def check(self, *args, **kwargs):
        return all(policy.check(*args, **kwargs) for policy in self.policies)


class InvariantLayer:
    """A named layer of invariant rules."""

    def __init__(self, rules, name=None):
        self.rules = rules
        self.name = name

    def check(self, *args, **kwargs):
        return all(rule(*args, **kwargs) for rule in self.rules)


def ALL(*policies):
    return CompositePolicy(list(policies))


def LAYER(name, *rules):
    return InvariantLayer(list(rules), name=name)
