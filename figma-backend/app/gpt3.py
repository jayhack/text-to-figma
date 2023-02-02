import openai

# EDIT ME
print('Change your OpenAI Key!')
openai.api_key = 'sk-ABCDEFGHIJKLMNOP'



class GPT3(object):
    """Handles interface with the model, including translation back and forth (?) from YAML"""

    @staticmethod
    def _generate(prompt: str) -> str:
        print('[GPT3] Generating...')
        response = openai.Completion.create(
            model="code-davinci-002",
            prompt=prompt,
            temperature=0,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response['choices'][0]['text']

    @classmethod
    def generate_yaml(cls, prompt: str) -> str:
        raw_gen = cls._generate(prompt)
        yaml_str = raw_gen.split('```')[0]
        return yaml_str
