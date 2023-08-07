import os
import json
from prefect import task, flow 
from tqdm import tqdm  
import copy

from wopo.prompts import Prompts
from wopo.agent import Agent 
from wopo.consolidator import Consolidator
from wopo.minifier import EntropyMinifier

class WOPO:
    def __init__(self, prompt, data, text_gen_func = None, strategy: str = "max", process_verbose: bool = False):
        self.agents = [Agent(prompt, datapoint["context"], datapoint["output"], text_gen_func) for datapoint in data]
        self.prompter = Prompts(text_gen_func)
        
        assert text_gen_func is not None, "Text Generation Function not provided"
        self.text_gen = copy.deepcopy(text_gen_func)

        self.optimal_prompt = None 
        self.consolidator = Consolidator(strategy = strategy)

    def run_optimisation(self, num_iters: int = 1, num_steps_per_iter: int = 1, top_k: int = 1, random_sample_size: int = 1, cutoff_score: int = 100, retries_on_failure: int = 3, retry_delay_seconds: int = 15): 

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
            correctness_levels = check_correctness_for_agent.map(self.agents)
            return correctness_levels

        for i in tqdm(range(num_iters)):
            
            for step in range(num_steps_per_iter):
                run_the_step()
        
            correctness_scores = correctness()
            correctness_scores = [a.result() for a in correctness_scores]
            consolidated_prompt, step_results = self.consolidator.consolidate(top_k, random_sample_size, correctness_scores)#consolidate_scores(correctness_scores)
            
            agent_states[i] = [agent.logs() for agent in self.agents]

            if step_results['min'] >= cutoff_score:
                print(f"Early stopping at step {i}, minimum score is {step_results['min']}")
                break

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
        return agent.prompt, agent.logs()

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

    def minify(self, minification_model: str = 'bert-base-uncased', percentile: int = 0.1):
        minifier = EntropyMinifier(model_name = minification_model, p = probability)

        return minifier.minify(self.optimal_prompt)

