# -*- coding: utf-8 -*-
import torch
from chatbot_agent.interface.policy import Policy
from chatbot_agent.policy.rule_based_multiwoz_bot import RuleBasedMultiwozBot
from chatbot_agent.policy.policy_agenda_multiwoz import UserPolicyAgendaMultiWoz

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class RulePolicy(Policy):

    def __init__(self, goal_model_path, db_path, vocab_path, is_train=False, character='sys'):
        self.is_train = is_train
        self.character = character

        if character == 'sys':
            self.policy = RuleBasedMultiwozBot(db_path)
        elif character == 'usr':
            self.policy = UserPolicyAgendaMultiWoz(goal_model_path, db_path, vocab_path)
        else:
            raise NotImplementedError('unknown character {}'.format(character))

    def predict(self, state):
        """
        Predict an system action given state.
        Args:
            state (dict): Dialog state. Please refer to util/state.py
        Returns:
            action : System act, with the form of (act_type, {slot_name_1: value_1, slot_name_2, value_2, ...})
        """
        return self.policy.predict(state)

    def init_session(self, **kwargs):
        """
        Restore after one session
        """
        self.policy.init_session(**kwargs)

    def is_terminated(self):
        if self.character == 'sys':
            return None
        return self.policy.is_terminated()

    def get_reward(self):
        if self.character == 'sys':
            return None
        return self.policy.get_reward()

    def get_goal(self):
        if hasattr(self.policy, 'get_goal'):
            return self.policy.get_goal()
        return None
