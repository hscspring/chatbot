# README

## 实验步骤

### 了解数据

通过阅读论文《MultiWOZ 2.1: A Consolidated Multi-Domain Dialogue Dataset with State Corrections and State Tracking Baselines》了解数据基本结构。

### 了解评估方法

通过阅读论文《ConvLab-2: An Open-Source Toolkit for Building, Evaluating, and Diagnosing Dialogue Systems》了解如何评估一个对话系统。

### 重构评估 Agent

ConvLab-2 使用 sys_content 训练数据训练一个模拟器作为 user 角色对对话系统能力进行模拟评估。通过阅读源代码，将这部分内容单独重构为一个模块，使用方法如下：

```python
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
```

运行 `damd` 作为 System Agent，以 100 次对话为例：

```python
sys_agent = Damd(
    vocab_path=os.path.join(root, "data/damd/vocab"),
    data_path=os.path.join(root, "data/damd/data_processed"),
    db_processed_path=os.path.join(root, "data/damd/db_processed"),
    model_path=os.path.join(root, "model/damd/all_aug_sample3_sd777_lr0.005_bs80_sp5_dc3")
)

analyzer.sample_dialog(sys_agent)
analyzer.comprehensive_analyze(sys_agent=sys_agent, model_name='DAMD', total_dialog=100)
```

结果如下：

![](images/damd.png)

### 阅读论文

分别阅读论文，了解思想和算法。

- SimpleTOD: A Simple Language Model for Task-Oriented Dialogue：使用 GPT2 训练端到端模型
- UBAR: Towards Fully End-to-End Task-Oriented Dialog System with GPT-2：相比 SImpleTOD，上下文增加考虑了 Belief State，DataBase Result，System Action

### 训练模型

需要将原来的 2.0 版本数据调整为 2.1 版本。

#### simpletod

训练代码：

```bash
$ zsh train_end2end.sh cpu gpt2 gpt2-tiny 2
```

![](images/simpletod.png)

#### ubar

训练代码：

```bash
$ python3 train.py -mode train -cfg gpt_path=distilgpt2 lr=1e-4 warmup_steps=2000 gradient_accumulation_steps=16 batch_size=2 epoch_num=60 exp_no=best_model
```

![](images/ubar.png)

### 评估推理

使用之前构建好的 `chatbot_agent` 作为 user，新的模型作为 system（可参考之前的 damd），完成自动交互评估测试。

## 附录

### 项目整体目录

```bash
├── chatbot
├── damd
├── simpletod
└── ubar
```

### chatbot 目录

```bash
.
├── README.md
├── chatbot_agent
│   ├── README.md
│   ├── chatbot_agent
│   └── setup.py
├── data
│   ├── agent
│   ├── damd
│   ├── simpletod
│   └── ubar
├── e2e_dialog
│   ├── README.md
│   ├── damd
│   ├── setup.py
│   ├── simpletod
│   └── ubar
├── eval
│   ├── __pycache__
│   ├── damd.py
│   ├── results
│   ├── simpletod.py
│   ├── ubar.py
│   ├── user.py
│   └── user.pyc
├── images
│   ├── damd.png
│   ├── simpletod.png
│   └── ubar.png
├── model
│   ├── damd
│   ├── goal
│   ├── simpletod
│   ├── sys_context
│   └── ubar
└── requirements.txt
```

### 使用指南

```bash
$ pip install -r requirements.txt
$ cd chatbot_agent
$ pip install -e .
$ cd e2e_dialog
$ pip install -e .
```

