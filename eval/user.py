import os
import random
import numpy as np
import torch

from chatbot_agent.nlu import BERTNLU
from chatbot_agent.policy.rule import RulePolicy
from chatbot_agent.nlg import TemplateNLG
from chatbot_agent.agent import PipelineAgent
from chatbot_agent.analyzer import Analyzer


def set_seed(r_seed):
    random.seed(r_seed)
    np.random.seed(r_seed)
    torch.manual_seed(r_seed)

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("root: ", root)

user_nlu = BERTNLU(
    model_dir=os.path.join(root, "model/sys_context"),
    vocab_dir=os.path.join(root, "data/agent/vocab"),
)
user_dst = None
user_policy = RulePolicy(
    goal_model_path=os.path.join(root, "model/goal/new_goal_model.pkl"),
    db_path=os.path.join(root, "data/agent/db"),
    vocab_path=os.path.join(root, "data/agent/vocab/"),
    character="usr",
)

user_nlg = TemplateNLG(
    is_user=True, 
    template_dir=os.path.join(root, "data/agent/template")
)

user_agent = PipelineAgent(user_nlu, user_dst, user_policy, user_nlg, name='user')
analyzer = Analyzer(
    db_path=os.path.join(root, "data/agent/db"), 
    user_agent=user_agent, 
    dataset='multiwoz'
)


text = "How about rosa's bed and breakfast ? Their postcode is cb22ha."
nlu_res = user_nlu.predict(text)
print(nlu_res)