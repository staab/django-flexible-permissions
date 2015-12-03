from flexible_permissions._utils import ensure_plural

_agent_registry = {}


def register_agent(cls, get_related_agents):
    """
    Register class function pair to get related agents.
    get_related_agents takes an agent and returns other agents
    that that agent implies. This should be used for getting
    groups from a user, for example.
    """
    _agent_registry[cls] = get_related_agents


def normalize_agent(agents, infer_agents=True):
    """
    Turn an agent into a list of equivalent agents
    """
    result = []
    for agent in ensure_plural(agents):
        if agent.__class__ not in _agent_registry:
            raise KeyError("%s is not registered." % agent.__class__)

        # Delegate agent calculation to registered function
        if infer_agents:
            result += list(_agent_registry[agent.__class__](agent))
        else:
            result.append(agent)

    return list(set(result))
