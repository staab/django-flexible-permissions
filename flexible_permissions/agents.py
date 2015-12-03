from permissions.utils import NULL, normalize_value

_agent_registry = {}


def register_agent(cls, get_related_agents):
    """
    Register class function pair to get related agents.
    get_related_agents takes an agent and returns other agents
    that that agent implies. This should be used for getting
    groups from a user, for example.
    """
    _agent_registry[cls] = get_related_agents


def normalize_agent(agents, **kwargs):
    """
    Turn an agent into a list of equivalent agents
    """
    infer_agents = kwargs.pop('infer_agents', True)

    agents = normalize_value(agents)

    # Agent being NULL is special. That means match on isnull instead.
    if len(agents) == 1 and agents[0] is NULL:
        return NULL

    result = []
    for agent in agents:
        # Delegate agent calculation to registered function
        if infer_agents:
            if agent.__class__ not in _agent_registry:
                raise KeyError("%s is not registered." % agent.__class__)

            result += list(_agent_registry[agent.__class__](agent))
        else:
            result.append(agent)

    return list(set(result))
