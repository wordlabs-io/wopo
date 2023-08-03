import os
import json
from prefect import task, flow 
from wopo.prompts import Prompts
from wopo.agent import Agent 
import pandas as pd
from tqdm import tqdm  

class WOPO:
    def __init__(self, prompt, data, text_gen_func = None, process_verbose: bool = False):
        self.agents = [Agent(prompt, datapoint["context"], datapoint["output"], text_gen_func) for datapoint in data]
        self.prompter = Prompts()
        
        assert text_gen_func is not None, "Text Generation Function not provided"
        self.text_gen = text_gen_func

        self.optimal_prompt = None 

    def run_optimisation(self, mode: str = "brute_force", num_iters: int = 1, num_steps_per_iter: int = 1, top_k: int = 1, retries_on_failure: int = 3, retry_delay_seconds: int = 15): 

        results = {}
        agent_states = {}

        @task(retries = retries_on_failure, retry_delay_seconds = retry_delay_seconds) 
        def run_one_step_for_agent(a):
            a.prompt_step()
                    
        @task(retries = retries_on_failure, retry_delay_seconds = retry_delay_seconds)
        def check_correctness_for_agent(a):
            return a.log_last_step()

        @flow(retries = retries_on_failure, retry_delay_seconds = retry_delay_seconds) 
        def run_the_step():
            run_one_step_for_agent.map(self.agents)

        @flow(retries = retries_on_failure, retry_delay_seconds = retry_delay_seconds)
        def correctness():
            temp = check_correctness_for_agent.map(self.agents)
            return temp
   
        def consolidate_scores(agent_scores):
            df = pd.DataFrame.from_dict(agent_scores)
            avg_score = df["score"].mean()
            min_score = df["score"].min()
            max_score = df["score"].max()

            results = {
                "avg": avg_score,
                "max": max_score,
                "min": min_score
            }

            df = df.nlargest(top_k, "score")
            df = df["prompt"]
            prompt_list = df.tolist()
            if len(prompt_list) > 1:
                consolidate_prompt = self.prompter.consolidation_prompt(prompt_list)
                consolidate_prompt = self.text_gen(consolidate_prompt)
            else:
                consolidate_prompt = prompt_list[0]

            return consolidate_prompt, results


        for i in tqdm(range(num_iters)):
            
            for step in range(num_steps_per_iter):
                run_the_step()
        
            correctness_scores = correctness()
            correctness_scores = [a.result() for a in correctness_scores]
            consolidated_prompt, step_results = consolidate_scores(correctness_scores)
            
            agent_states[i] = [agent.logs() for agent in self.agents]

            self.agents = [agent.flush(consolidated_prompt) for agent in self.agents]
            
            results[i] = step_results

        self.optimal_prompt = consolidated_prompt
        return consolidated_prompt, results, agent_states

    def run_single_chain_optimisation(self, num_iters: int = 1, stop_at_score: int = 100):
        assert len(self.agents) == 1, "There is more than one agent. You should use the YAPO.run_optimisation() function instead"
        
        agent = self.agents[0]

        for i in tqdm(range(num_iters)):
            agent.prompt_step()
            if agent.log_last_step()["score"] >= stop_at_score:
                print(f"Early stopping at step {i}")
                break
        self.optimal_prompt = agent.prompt 
        return agent.prompt

    def run_test(self, data, save_location: str = None):
        assert self.optimal_prompt is not None, "Optimal prompt not provided or found"
        df_data = []

        for d in data:
            prompt = self.prompter.execute_prompt(self.optimal_prompt, d["context"])
            extracted_data = self.text_gen(prompt)

            correctness_prompt = self.prompter.correctness_prompt(d["output"], extracted_data)
            correctness_info = self.text_gen(correctness_prompt)
            correctness_info = json.loads(correctness_info)

            df_data_dict = {
                "correct_output": d["output"],
                "received_output": extracted_data,
                "score": correctness_info["correctness"],
                "feedback": correctness_info["explanation"]
            }
            df_data.append(df_data_dict)
        
        df = pd.DataFrame.from_dict(df_data)
        df.to_csv(save_location)

        return df




