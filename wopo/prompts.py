import copy

class Prompts:

    def __init__(self, generation_function = None):
        #assert generation_function is not None, "Text generation not provided, initialisation failed"
        self.generation_function = copy.deepcopy(generation_function)

    def initial_prompt(self, prompt: str, data: str = None):
        prompt = f"""
        Design a prompt in the following format: "Acting as a [role], [task]". The task is being performed on the data called context. Be as clear and detailed in the steps as possible. The entire prompt must be a single paragraph
        The task is as follows: {prompt}
        And the context for the task is as follows: {data}
        """
        return prompt

    def update_prompt_with_feedback(self, prompt: str, data: str, expected_output: str, received_output: str, feedback: str):
        prompt = f"""
        You are a prompt engineer. When the following prompt was used on the specific data called data, we receieved output received_output. However, the expected output was expected_output. Rewrite the prompt to better align the data with expected_output based on the feedback provided. The expected prompt should contain instructions in English and should not involve any code

        prompt: {prompt}
        data: {data}
        expected_output: {expected_output}
        received_output: {received_output}
        feedback: {feedback}
        """
        return self.generation_function(prompt)
    
    def execute_prompt(self, prompt:str, data: str):
        prompt = f"""
        {prompt}

        {data}
        """
        return self.generation_function(prompt)

    def clean_prompt(self, prompt: str):
        prompt = f"""
        Given this prompt, only retain steps relevant to the prompt

        prompt: {prompt}
        """

        return self.generation_function(prompt)

    def correctness_prompt(self, expected_output: str, received_output: str):
        prompt = f"""
        Compare these two answers. Give them a score between 0 and 100 for similarity. The response must be a JSON string with keys correctness: score, and explanation: contains explanation for why these two are different

        expected_output: {expected_output}

        received_output: {received_output}
        """
        return self.generation_function(prompt)

    def consolidation_prompt(self, prompts_list):
        prompts = "\n\n".join(prompts_list)

        prompt = f"""
        You are a prompt engineer. Extract all unique points from all the prompts. Then combine all these prompts into one single prompt that is a single paragraph. Only return the combined prompt

        {prompts}
        """

        return self.generation_function(prompt)

    def execute(self, prompt):
        return self.generation_function(prompt)
