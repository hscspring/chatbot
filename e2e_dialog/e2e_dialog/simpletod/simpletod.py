from chatbot_agent.agent import Agent
import torch
from transformers import (
    GPT2Tokenizer,
    GPT2LMHeadModel
)

from .database import MultiWozDB, lexicalize_train, lexicalize_hotel

device = "cpu"

class SimpleTod(Agent):

    def __init__(self, data_path, model_path, decoding="greedy", max_len=1024):
        self.db = MultiWozDB(data_path)
        self.tk = GPT2Tokenizer.from_pretrained(model_path)
        self.break_tokens = self.tk.encode(self.tk._eos_token + " !" + " ?")
        self.md = GPT2LMHeadModel.from_pretrained(model_path)
        self.md.eval()
        self.md.to(device)
        self.context = ""
        self.domain_queue = []
        self.decoding = decoding
        self.max_len = max_len
        self.name = "simpletod"


    def init_session(self):
        self.context = ""
        
    
    def build_input(self, user_inp):
        user = '<|user|> {}'.format(user_inp)
        self.context = self.context + ' ' + user
        text = '<|endoftext|> <|context|> {} <|endofcontext|>'.format(self.context)
        return text.strip()
    
    def response(self, inp):
        text = self.build_input(inp)
        indexed_tokens = self.tk.encode(text)
        if len(indexed_tokens) > self.max_len:
            indexed_tokens = indexed_tokens[-self.max_len:]
        tokens_tensor = torch.tensor([indexed_tokens]).to(device)
        predicted_index = indexed_tokens[-1]

        if self.decoding == 'nucleus':
            sample_output = self.md.generate(
                tokens_tensor,
                do_sample=True,
                max_length=self.max_len,
                top_p=0.5,
                top_k=0
            )
            predicted_text = self.tk.decode(sample_output[0])
            tmp = ' '.join([predicted_text.split('<|endofresponse|>')[0], '<|endofresponse|>'])
            predicted_text = tmp

        elif self.decoding == 'greedy':
            # sample_output = self.md.generate(
            #     tokens_tensor,
            #     max_length=self.max_len,
            #     do_sample=False
            # )
            # predicted_text = self.tk.decode(sample_output[0], skip_special_tokens=True)
            while predicted_index not in self.break_tokens:
                outputs = self.md(tokens_tensor)
                predictions = outputs[0]
                predicted_index = torch.argmax(predictions[0, -1, :]).item()
                indexed_tokens.append(predicted_index)
                
                # sometime model generate repeated actions, we just use truncate actions if this happens
                predicted_text = self.tk.decode(indexed_tokens)
                if '<|action|>' in predicted_text:
                    generated_actions = predicted_text.split('<|action|>')[-1].split('<|endofaction|>')[0].split(',')
                    new_actions = []
                    for a in generated_actions:
                        if a in ['', ' ']:
                            continue
                        new_actions.append(a.strip())
                    len_actions = len(new_actions)
                    if len(list(set(new_actions))) > len(new_actions) or (len_actions > 10 and not truncate_action):
                        actions = '<|action|> {} <|endofaction|>'.format(' , '.join(list(set(new_actions))))
                        indexed_tokens = self.tk.encode('{} {}'.format(predicted_text.split('<|action|>')[0], actions))
                        truncate_action = True

                tokens_tensor = torch.tensor([indexed_tokens]).to(device)
                if len(indexed_tokens) > self.max_len:
                    break
                if self.tk.decode(indexed_tokens).endswith('<|endofresponse|>'):
                    break
                    
            predicted_text = self.tk.decode(indexed_tokens)
            tmp = ' '.join([predicted_text.split('<|endofresponse|>')[0], '<|endofresponse|>'])
            predicted_text = tmp

        response_text = self.get_response_new(predicted_text)
        system = '<|system|> {}'.format(response_text)
        self.context = self.context + ' ' + system
        
        print("predicted_text: ", predicted_text)
        print("response_text: ", response_text)
        # print(self.domain_queue)
        return system
    
    def response_search(self, inp):
        text = self.build_input(inp)
        indexed_tokens = self.tk.encode(text)
        if len(indexed_tokens) > self.max_len:
            indexed_tokens = indexed_tokens[-self.max_len:]
        tokens_tensor = torch.tensor([indexed_tokens]).to(device)
        predicted_index = indexed_tokens[-1]

        with torch.no_grad():
            while predicted_index not in self.break_tokens:
                outputs = self.md(tokens_tensor)
                predictions = outputs[0]
                predicted_index = torch.argmax(predictions[0, -1, :]).item()
                indexed_tokens.append(predicted_index)
                tokens_tensor = torch.tensor([indexed_tokens]).to(device)
                if len(indexed_tokens) > self.max_len:
                    break
                if self.tk.decode(indexed_tokens).endswith('<|endofbelief|>'):
                    break
        
        tmp_pred = self.tk.decode(indexed_tokens)
        belief_text_list = self.get_belief_new_dbsearch(tmp_pred)
        belief_dict = self.convert_belief(belief_text_list)
        domain = self.get_turn_domain(belief_dict)

        truncate_action = False
        with torch.no_grad():
            while predicted_index not in self.break_tokens:
                outputs = self.md(tokens_tensor)
                predictions = outputs[0]
                predicted_index = torch.argmax(predictions[0, -1, :]).item()
                indexed_tokens.append(predicted_index)
                if len(indexed_tokens) > self.max_len:
                    break
                predicted_text = self.tk.decode(indexed_tokens)
                if '<|action|>' in predicted_text:
                    generated_actions = predicted_text.split('<|action|>')[-1].split('<|endofaction|>')[0].split(',')
                    new_actions = []
                    for a in generated_actions:
                        if a in ['', ' ']:
                            continue
                        new_actions.append(a.strip())
                    len_actions = len(new_actions)
                    if len(list(set(new_actions))) > len(new_actions) or (len_actions > 10 and not truncate_action):
                        actions = '<|action|> {} <|endofaction|>'.format(' , '.join(list(set(new_actions))))
                        indexed_tokens = self.tk.encode('{} {}'.format(predicted_text.split('<|action|>')[0], actions))
                        truncate_action = True
                tokens_tensor = torch.tensor([indexed_tokens]).to(device)

        predicted_text = self.tk.decode(indexed_tokens)
        response_text = self.get_response_new(predicted_text)

        lex_response = ""
        db_results = []
        if domain in belief_dict:
            db_results = self.db.queryResultVenues_new(domain, belief_dict[domain], real_belief=True)

            if domain == 'train':
                lex_response = lexicalize_train(response_text, db_results, belief_dict, turn_domain=domain)
            elif domain == 'hotel':
                lex_response = lexicalize_hotel(response_text, db_results, belief_dict, turn_domain=domain)

        if not lex_response:
            system = '<|system|> {}'.format(response_text)
        else:
            system = '<|system|> {}'.format(lex_response)
        self.context = self.context + ' ' + system
        
        print("belief_dict: ", belief_dict)
        print("belief_text_list: ", belief_text_list)
        print("domain: ", domain)
        print("predicted_text: ", predicted_text)
        print("response_text: ", response_text)
        print("db_results: ", db_results)
        print(self.domain_queue)
        return system

    def get_response_new(self, sent):
        if '<|response|>' in sent:
            tmp = sent.split('<|belief|>')[-1].split('<|action|>')[-1].split('<|response|>')[-1]
        else:
            return ''
        tmp = tmp.strip(' .,')
        tmp = tmp.replace('<|endofresponse|>', '')
        tmp = tmp.replace('<|endoftext|>', '')
        tokens = self.tk.encode(tmp)
        new_tokens = []
        for tok in tokens:
            if tok in self.break_tokens:
                continue
            new_tokens.append(tok)
        response = self.tk.decode(new_tokens).strip(' ,.')
        return response

    def get_turn_domain(self, beliefs):
        for k in beliefs.keys():
            if k not in self.domain_queue and k in self.db.domains:
                self.domain_queue.append(k)
                turn_domain = k
                return turn_domain
        return self.domain_queue[-1]
    
    def convert_belief(self, belief):
        dic = {}
        for bs in belief:
            if bs in [' ', '']:
                continue
            tmp = bs.split(" ")
            if len(tmp) < 2:
                continue
            domain = tmp[0]
            slot = tmp[1]
            if slot == 'book':
                slot = ' '.join(bs.split(' ')[1:3])
                value = ' '.join(bs.split(' ')[3:])
            else:
                value = ' '.join(bs.split(' ')[2:])
            if domain not in dic:
                dic[domain] = {}
            try:
                dic[domain][slot] = value
            except:
                print(domain)
                print(slot)
        return dic

    def get_belief_new_dbsearch(self, sent):
        if '<|belief|>' in sent:
            tmp = sent.strip(' ').split('<|belief|>')[-1].split('<|endofbelief|>')[0]
        else:
            return []
        tmp = tmp.strip(' .,')
        tmp = tmp.replace('<|endofbelief|>', '')
        tmp = tmp.replace('<|endoftext|>', '')
        belief = tmp.split(',')
        new_belief = []
        for bs in belief:
            bs = bs.strip(' .,')
            if bs not in new_belief:
                new_belief.append(bs)
        return new_belief


if __name__ == '__main__':

    import os
    root = "/Users/Yam/Yam/chatbot/chatbot/"

    sd = SimpleTod(
        data_path = os.path.join(root,  "data/simpletod"),
        model_path = os.path.join(root, "model/simpletod/gpt2-small/checkpoint-111"),
        max_len=512
    )

    text1 = "hi , could you help me with my plans ? i am looking for a train ."
    text2 = "hello"
    text3 = "how are you ?"
    text4 = "can you help me ?"

    print("USER: ", text1)
    sd.response(text1)
    print("="*50)