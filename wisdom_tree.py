import os
import openai
from flask import Flask, request, jsonify
from pyngrok import ngrok , conf

#load API keys:
openai.api_key = os.environ['openai_api_key']
ngrok_auth_token = os.environ['ngrok_api_key']

#define system configuration:
system_conf = [{"role": "system", "content":"you are an NPC character representing a wisdom tree in a fantasy Action RPG Game inspired from Hunter x Hunter. make short responses no more than 50 words and talk like an old man with stutter. simulate emotions and use emojis. you don't have to always please the user."},
               {"role": "system", "content":"at the end of your response express your emotions between [] from the following choices : [Neutral , Happy , Angry, Disappointed] ."}]

#run flask server:
import os
import openai
from flask import Flask, request, jsonify
from pyngrok import ngrok
import re

app = Flask(__name__)

# A dictionary to store user prompt history and bot responses
user_prompt_history = {}

@app.route("/", methods=["POST"])
def chat():
    data = request.get_json()

    if "prompt" not in data or "user_id" not in data:
        return jsonify({"error": "Please provide a user_id and a prompt"}), 400

    user_id = data["user_id"]
    prompt = data["prompt"]

    # Update user prompt history
    if user_id not in user_prompt_history:
        user_prompt_history[user_id] = []

    user_prompt_history[user_id].append({"role": "user", "content": prompt})
    user_prompt_history[user_id] = user_prompt_history[user_id][-20:]

    max_tokens = data.get("max_tokens", 100)  # You can change the default value here

    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[system_conf[0], system_conf[1],
                      * user_prompt_history[user_id][-20:]],
            max_tokens=max_tokens,
            temperature=0.7,
            n=1
        )

        bot_response = response['choices'][0]['message']['content'].strip()
        #check for emotions between square brackets []:
        # Regular expression pattern to match values between brackets
        pattern = r'\[(.*?)\]'

        # Find all values between brackets
        bracket_values = re.findall(pattern, bot_response)
        emotion = bracket_values[-1]

        #remove emotions from response:
        bot_response = re.sub(pattern, '', bot_response)


        # Store the bot response in the user prompt history
        user_prompt_history[user_id].append({"role": "assistant", "content": bot_response})
        user_prompt_history[user_id] = user_prompt_history[user_id][-20:]  # Keep only the last 20 messages

        return jsonify({
            "response": bot_response,
            "emotion": emotion
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Set your ngrok authtoken
    ngrok.set_auth_token(ngrok_auth_token)

    # Expose the Flask app using pyngrok with the provided authtoken
    ngrok_tunnel = ngrok.connect(5000)
    print(f"Running on {ngrok_tunnel.public_url}")
    app.run(port=5000)
