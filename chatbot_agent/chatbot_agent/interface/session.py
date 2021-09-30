from abc import ABC, abstractmethod


class Session(ABC):
    """Base dialog session controller, which manages the agents to conduct a complete dialog session.
    """

    @abstractmethod
    def next_agent(self):
        """Decide the next agent to generate a response.

        In this base class, this function returns the index randomly.

        Returns:
            next_agent (Agent): The index of the next agent.
        """
        pass

    @abstractmethod
    def next_response(self, observation):
        """Generated the next response.
        
        Args:
            observation (str or dict): The agent observation of next agent.
        Returns:
            response (str or dict): The agent's response.
        """
        pass

    @abstractmethod
    def init_session(self):
        """Init the agent variables for a new session."""
        pass
