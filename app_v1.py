import streamlit as st
import openai
import wikipediaapi
import time
import random
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Wikipedia API with a custom user agent
user_agent = "KumarPriyank/1.0 (kpriyank88@gmail.com)"  # Use your own app name and email

wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent=user_agent
)

# File to store AI-generated thoughts
DATASET_FILE = "thought_dataset.json"

# Load existing dataset or create a new one
try:
    with open(DATASET_FILE, "r") as f:
        thought_dataset = json.load(f)
except FileNotFoundError:
    thought_dataset = []

# Function to generate a thought
def generate_thought():
    topics = ["philosophy", "psychology", "physics", "AI ethics", "space travel", "consciousness", "time travel", "biology", "future technology"]
    topic = random.choice(topics)
    
    prompt = f"Think of a deep and logical thought about {topic}. Your response should always start with Thought_Title: followed by the appropriate Title or heading you would choose for you response. Expand on why it's interesting. Always end with a deep and profound question. Limit response to 100 words."
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a deep thinker."},
                  {"role": "user", "content": prompt}]
    )
    
    #return response["choices"][0]["message"]["content"]
    return response.choices[0].message.content.strip()

# Function to validate thought using Wikipedia
def validate_thought(thought):  # Take the first keyword to search Wikipedia
    st.write(f"❔ Let Look for: {thought}")
    page = wiki.page(thought)
    
    if page.exists():
        return f"VALID: Found relevant Wikipedia article on '{thought}'.\nSummary: {page.summary[:500]}...", True
    else:
        return "INVALID: No reliable source found.", False
    
# Function to validate thought using Wikipedia
def validate_thought_open_ai(thought):
    
    prompt = f"Tell me about: {thought}. Limit response to 200 words. Always start your response with either VALID: or INVALID: tag based on whether you think the topic or query is correct and complete contextually"
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You answer question."},
                  {"role": "user", "content": prompt}]
    )
    
    responseText=response.choices[0].message.content.strip()

    if responseText.startswith("VALID:"):
        return f"{responseText}", True
    else:
        return f"INVALID: No reliable source found.", False

# Function to expand thought
def expand_thought(thought):
    prompt = f"Expand on this thought and take it further logically: {thought}. Try to reason with the data you have."
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a deep thinker."},
                  {"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content.strip()

# Streamlit UI
st.title("🤖 AI Thought Engine")
st.write("The AI will continuously generate, validate, and expand thoughts while building its own dataset.")

# Start AI thinking process
if st.button("Start Thinking"):
    thought_count = 0
    while True:
        thought_count += 1
        st.subheader(f"💭 Thought #{thought_count}")

        # Generate thought
        thought = generate_thought()
        st.write(f"😕 **AI Thought:**")
        st.write(f"{thought}")

        #Extract Thought title
        toValidate_start = thought.find("Thought_Title: ") + 15
        toValidate_end = thought.find("\n", toValidate_start)
        toValidate_text = thought[toValidate_start:toValidate_end]

        # Validate thought
        validation, is_valid = validate_thought_open_ai(toValidate_text)

        if is_valid:
            validation_start = validation.find("VALID: ") + 7
            validation_end = validation.find("\n", validation_start)
            validation_text = validation[validation_start:validation_end]
            st.write(f"✅ **Valid Thought!** {validation_text}")
        else:
            validation_start = validation.find("INVALID: ") + 9
            validation_end = validation.find("\n", validation_start)
            validation_text = validation[validation_start:validation_end]
            st.write(f"❎ **Invalid Thought!** {validation_text}")
       
        summary_start = validation.find("Summary: ") + 9
        summary_end = validation.find(")", summary_start)
        summary_text = validation[summary_start:summary_end]

        # Split summary text into words
        words = summary_text.split()

        # Make first word bold
        first_word = f"**{words[0]}**"
        remaining_words = " ".join(words[1:])

        # Join bold first word with remaining words
        bold_summary_text = f"{first_word} {remaining_words}"

        st.write(bold_summary_text)

        # Expand thought
        new_thought = expand_thought(thought)
        st.write(f"💭 **Expanded Thought:**")
        st.write(f"{new_thought}")

        # Store data for fine-tuning
        thought_entry = {
            "thought": thought,
            "expanded_thought": new_thought,
            "validation": validation,
            "valid": is_valid
        }

        thought_dataset.append(thought_entry)

        # Save dataset incrementally
        with open(DATASET_FILE, "w") as f:
            json.dump(thought_dataset, f, indent=4)

        st.write("📓 Thought saved for fine-tuning.")

        # Pause before next thought cycle
        time.sleep(10)
