from wopo.prompts import Prompts
import json 

class Agent:
    def __init__(self, prompt: str = None, data: str = None, correct_output: str = None, text_gen = None):
        self.prompt = prompt
        self.original_prompt = prompt 
        self.data = data 
        self.correct_output = correct_output
        self.prompt_funcs = Prompts()
        self.last_output = None
        self.last_feedback = None
        self.step = 0
        self.state = []
        self.text_gen = text_gen

    
    def update_state(self, prompt: str = None, output: str = None, feedback: str = None, score: int = None):
        self.prompt = prompt
        self.last_output = output
        self.last_feedback = feedback        
        update_dict = {
            self.step: {
                "prompt": prompt,
                "output": output,
                "feedback": feedback,
                "score": score
            }
        }
       
        self.state.append(update_dict)

        self.step += 1
 
    def generate_prompt_and_output(self, prompt):
        receive_prompt = self.text_gen(prompt)

        clean_prompt = self.prompt_funcs.clean_prompt(receive_prompt)
        clean_prompt = self.text_gen(clean_prompt)    
        
        receive_output = self.prompt_funcs.execute_prompt(clean_prompt, self.data)
        receive_output = self.text_gen(receive_output)

        return clean_prompt, receive_output


    def prompt_step(self):
        if self.step == 0:
            design_prompt = self.prompt_funcs.initial_prompt(self.prompt, self.data)
            prompt, output = self.generate_prompt_and_output(design_prompt)
            correctness_check = self.check_correctness(output)
            feedback = correctness_check["explanation"]
            score = correctness_check['correctness']
            self.update_state(prompt, output, feedback, score)
            
        else:
            design_prompt = self.prompt_funcs.update_prompt_with_feedback(self.prompt, self.data, self.correct_output, self.last_output, self.last_feedback)
            prompt, output = self.generate_prompt_and_output(design_prompt)
            correctness_check = self.check_correctness(output)
            feedback = correctness_check["explanation"]
            score = correctness_check['correctness']

            last_step = self.log_last_step()
            if last_step["score"] <= score:
                self.update_state(prompt, output, feedback, score)

    
    def check_correctness(self, output):
        correctness_prompt = self.prompt_funcs.correctness_prompt(self.correct_output, output)
        response = self.text_gen(correctness_prompt)
        dictified = json.loads(response)
        return dictified

    def log_last_step(self):
        return self.state[-1][self.step - 1]
    
    def logs(self):
        return self.state

    def flush(self, new_prompt: str = None):
        if new_prompt is None: 
            self.prompt = self.original_prompt
        else: 
            self.prompt = new_prompt

        self.state = []
        self.last_feedback = None
        self.last_output = None 
        self.step = 0

        return self