import os
from user import analyzer, set_seed, root
from e2e_dialog.damd import Damd

sys_agent = Damd(
    vocab_path=os.path.join(root, "data/damd/vocab"),
    data_path=os.path.join(root, "data/damd/data_processed"),
    db_processed_path=os.path.join(root, "data/damd/db_processed"),
    model_path=os.path.join(root, "model/damd/all_aug_sample3_sd777_lr0.005_bs80_sp5_dc3")
)

analyzer.sample_dialog(sys_agent)

set_seed(20200202)
analyzer.comprehensive_analyze(sys_agent=sys_agent, model_name='damd', total_dialog=100)
