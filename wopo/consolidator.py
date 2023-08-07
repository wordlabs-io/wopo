import pandas as pd
from wopo.prompts import Prompts 

class Consolidator:
    def __init__(self, strategy: str = "max", text_gen_func = None):
        self.strategy = strategy
        self.prompter = Prompts(text_gen_func)

    def combine_prompts(self, prompt_list):
        consolidate_prompt = self.prompter.consolidation_prompt(prompt_list)
        
    def consolidate(self, k: int = 1, random_sample_size: int = 1, agent_scores = None):
        df = pd.DataFrame.from_dict(agent_scores)
        avg_score = df["score"].mean()
        min_score = df["score"].min()
        max_score = df["score"].max()

        results = {
            "avg": avg_score,
            "max": max_score,
            "min": min_score
        }

        if self.strategy == 'max':
            df = df.nlargest(1, "score")

        elif self.strategy == 'top_k':
            df = df.nlargest(k, "score")

        elif self.strategy == 'random_from_top_k':
            df = df.nlargest(k, "score")
            df = df.sample(n = random_sample)

        df = df["prompt"]
        prompt_list = df.tolist()

        if len(prompt_list) > 1:
            consolidate_prompt = self.combine_prompts(prompt_list)
        else:
            consolidate_prompt = prompt_list[0]

        return consolidate_prompt, results
