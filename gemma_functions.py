import os
from dotenv import load_dotenv
import keras
import keras_nlp

# Load environment variables from .env file
load_dotenv()

# Access the variables
kaggle_username = os.getenv("KAGGLE_USERNAME")
kaggle_key = os.getenv("KAGGLE_KEY")

# Optionally print to check if they're loaded correctly (for debugging)
print(f"Kaggle Username: {kaggle_username}")
print(f"Kaggle Key: {kaggle_key}")

# Set Kaggle environment variables
os.environ["KAGGLE_USERNAME"] = kaggle_username
os.environ["KAGGLE_KEY"] = kaggle_key

# Set backend and memory handling
os.environ["KERAS_BACKEND"] = "jax"
os.environ["XLA_PYTHON_CLIENT_MEM_FRACTION"] = "1.00"

# Load the Gemma model
gemma_lm = keras_nlp.models.GemmaCausalLM.from_preset("gemma2_2b_en")
gemma_lm.summary()

# Inference
template = """{instruction} {response}"""
prompt = template.format(instruction="What should I do on a trip to Europe?", response="")

sampler = keras_nlp.samplers.TopKSampler(k=5, seed=2)
gemma_lm.compile(sampler=sampler)
print(gemma_lm.generate(prompt, max_length=256))
