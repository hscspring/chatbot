import os
from user import analyzer, set_seed, root
from e2e_dialog.simpletod import SimpleTod


sys_agent = SimpleTod(
    data_path = os.path.join(root,  "data/simpletod"),
    model_path = os.path.join(root, "model/simpletod/gpt2-small/checkpoint-111"),
    max_len=512
)

analyzer.sample_dialog(sys_agent)

set_seed(20200202)
analyzer.comprehensive_analyze(sys_agent=sys_agent, model_name='simpletod', total_dialog=10)
