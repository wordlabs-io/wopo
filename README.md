# wordlabs.io Open Prompt Optimiser (or WOPO)

## Need I introduce prompt optimisation?
Large Language Models (LLMs) are AI agents capable of performing specific tasks via natural language instruction on text based information. 

This makes them incredibly powerful. However, these machines lack idempotency 

> Idempotency: Given a question, the answer will always be the same. In math, 1 + 1 is always 2.
> The result of the add operation on any two real numbers is always idempotent.
> This, however, is not the case with LLMs, which may produce different results for the same question if asked twice

Additionally, finding the best possible prompt that incorporates a lot of different aspects of thinking is a labour of effort, not of intellect. This task can be better performed by prompt optimisation libraries. 

## WOPO: Usage 
### Prerequisites
WOPO uses Prefect for orchestration, however, PyPi was unable to find the right versions for installation. 
If not already installed, use the command below
```
pip install prefect==2.11.2 torch==2.0.1 transformers==4.31.0
```
Then install the WOPO library 
```
pip install wopo==0.0.1
```
> Please note that this library is still in alpha release, code for WOPO will be changing rapidly in the coming months.
> If you face any issues, make sure to drop a message here!

 ### Usage
```python
from wopo import WOPO

"""
For prompt optimisation, we basically need three things:
1. Initial Prompt
2. A set of context vs output (i.e. if operation prompt was performed on context, what would be the correct output>)
3. A selection strategy (to decide how to choose the right prompt

You will also need to pass a function that takes in a string and sends it to the LLM and returns the string.
Pass this function in the keyword argument text_gen_func
This keeps things simple and allows you to write any kind of function you'd like to interact with your LLM
"""
import openai 

openai.organisation = 'ORG-ID'
openai.api_key = 'API_KEY'

def generate_func(prompt, return_explanation = False):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": prompt}
        ]
    )
    resp_text = response['choices'][0]['message']['content']
    return resp_text

prompt = "Remove vowels"

#List of ip/op pairs with labels context and output
data = [
    {
        "context": "Sentence",
        "output" : "Sntnc"
    },
    {
        "context": "This is a sentence",
        "output" : "Ths s sntnc"
    }
]

#Initialise optimiser
y = WOPO(prompt, data, generate_func)

"""
num_iters: number of times we perform optimisation
num_steps_per_iter: number of times the prompt is updated in each step
top_k: at the end of each step, how many best prompts are selected to be merged into one
(this is being done so that the prompt generalises over multiple cases instead of specialising for one)

Returns:
optimal_prompt
results: scores of each step 
agent_states: complete logs of how each step changed the prompt and related feedback
"""
optimal_prompt, results, agent_states = y.run_optimisation(num_iters = 5, num_step_per_iter = 1, top_k = 2)

"""
You can also run simple tests to analyse how well the new prompt is working
The below function will return a Pandas DataFrame containing all the relevant information,
and also save the file to specified save location 
"""
test = y.run_test(some_other_data, save_location = "test_result.csv")
 ```

If you only have one ip/op pair, use ```WOPO.run_single_chain_optimisation()``` function. You may additionally specify the ```stop_at_score``` criteria (between 0-100) at which the chain can stop early

### Available selection strategies
1. Max: Choose the prompt that gets closest to the answer ```WOPO(strategy = 'max')```
2. Top K: Combine the prompts from the top k highest scoring prompts
   ```python
   WOPO(strategy = 'top_k')
   WOPO.run_optimisation(top_k = top_k)
   ```
3. Random Selection from Top K: Given top k scoring prompts, select n random prompts from the top k prompts
   ```python
   WOPO(strategy = 'random_from_top_k')
   WOPO.run_optimisation(top_k = top_k, random_sample_size = random_sample_size)
   ```
### Prompt Minification
Optimal prompts offer better accuracy in terms of output, but they tend to be verbose. Most LLMs are not cheap to operate, and it is best to use the fewest number of tokens possible in prompting. To reduce the number of tokens being used, we can simply find which words are most likely to be implicitly understood by the LLM even if they are removed.
> For example, if I were to say 'The quick brown fox' you immediately think of 'jumps over the lazy dog', even though 'ate all my peanut butter' was also a valid sentence
The process is called Entropy Minification.

```python
"""
Specify the model name (default: bert-base-uncased) from HuggingFace Transformers library and provide a percentile score (default: 0.1).
The tokens falling in the top percentile score of likelihood will be removed 
"""
optimal_prompt, _, _ = WOPO.run_optimisation()
minified_prompt = WOPO.minify(model_name = model_name, percentile = percentile)
```



