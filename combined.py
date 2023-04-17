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

    if "prompt" not in data or "user_id" not in data or "request_type" not in data:
        return jsonify({"error": "Please provide a user_id , a prompt, and a request_type."}), 400

    user_id = data["user_id"]
    prompt = data["prompt"]
    request_type = data["request_type"]
    max_tokens = data.get("max_tokens") 
    if request_type == "tree":
      # Update user prompt history
      if user_id not in user_prompt_history:
          user_prompt_history[user_id] = []

      user_prompt_history[user_id].append({"role": "user", "content": prompt})
      if len(user_prompt_history[user_id]) > 20:
        user_prompt_history[user_id] = user_prompt_history[user_id][-20:]


      try:
          response = openai.ChatCompletion.create(
              model='gpt-3.5-turbo',
              messages=[system_conf[0], system_conf[1],
                        * user_prompt_history[user_id]],
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
          emotion = bracket_values[-1] if bracket_values else "Neutral"

          #remove emotions from response:
          bot_response = re.sub(pattern, '', bot_response)


          # Store the bot response in the user prompt history
          user_prompt_history[user_id].append({"role": "assistant", "content": bot_response})

          return jsonify({
              "response": bot_response,
              "emotion": emotion
          })

      except Exception as e:
          return jsonify({"error": str(e)}), 500
    
    elif request_type == "intro":
      intro_conf = [{"role": "system", "content":f"The user will write his character backstory as part of a fantasy RPG game. Please  update below game introduction based on player backstory , make it short and use informal fantasy language:"},
                  {"role": "system", "content":f"{user_id} is born in a small village located at an isolated little island called : \"Whale Island\". Since he was able to walk , {user_id}  was daring , adventurous and always following his father's footsteps. One day when was not old enough to remember , his mother and father disappeared. He continued to live in their house and been looked after by his grandmother and auntie. {user_id} is now 15 years old , and he is more dependable than ever. He started exploring far parts of his island with a burning thought in his mind : \"I want to see and feel the wide open world!\""}]
      nen_conf = [{"role": "system", "content":"You are a system part of an Action RPG game inspired by Hunter x Hunter. you are responsible of determining a player Nen type based on his personality and background story. the output should be on of these choices : [Enhancer , Transmuter ,  Emitter ,  Conjurers ,  Manipulator , Specialist]. use below info to decide Nen type :"},
                    {"role": "system", "content":"- Enhancers are simple and determined. Most of them never lie, hide nothing, and are very straightforward in their actions or in their thinking. Their words and actions are often dominated by their feelings. They are generally very selfish and focused on their goals. This is reflected in their Nen as Enhancers typically rely on simple and uncomplicated Nen abilities.- Transmuters are whimsical, prone to deceit, and fickle. They have unique characteristics, and many are regarded as weirdos or tricksters. They often put forth a facade while hiding the truer aspects of their personalities. Even when they don't hide their personalities, they rarely reveal their true intentions. Many Transmuters rely on techniques that give unique and unpredictable properties to their Nen that reflect their personalities.- Emitters are impatient, not detail-oriented, short-tempered, and quick to react in a volatile manner. They resemble Enhancers in their impulsivity, but the difference between them is that Emitters tend to calm down and forget more easily. Because of the nature of Emission, many Nen abilities created by Emitters are primarily long range.- Conjurers are typically high-strung or overly serious, stoic, and nervous. They are often on guard as to be cautious. They are very observant and logical, rarely falling into traps. Being able to analyze things calmly is the strength of Conjurers. Many of the items that Conjurers create are often used by them deliberately, practically, and logically.- Manipulators are argumentative and logical. They advance at their own pace and tend to want to keep their families and loved ones safe. On the other hand, when it comes to pursuing their own goals, they do not listen to what others might have to say about it. While Manipulators often use techniques that allow them to control their opponents, some choose an inanimate medium to control.- Specialists are independent and charismatic. They won't say anything important about themselves and will refrain from making close friends. However, because of their natural charisma that attracts others, they are always surrounded by many people."}]


      try:
          #get intro
          response_intro = openai.ChatCompletion.create(
              model='gpt-3.5-turbo',
              messages=[intro_conf[0], intro_conf[1],
                       {"role": "user", "content": prompt}],
              max_tokens=max_tokens,
              temperature=0.7,
              n=1
          )

          response_intro = response_intro['choices'][0]['message']['content'].strip()

          #get nen type:
          response_nen = openai.ChatCompletion.create(
              model='gpt-3.5-turbo',
              messages=[nen_conf[0], nen_conf[1],
                       {"role": "user", "content": prompt}],
              max_tokens=max_tokens,
              temperature=0.7,
              n=1
          )

          response_nen = response_nen['choices'][0]['message']['content'].strip()
          #check what nen type presented:
          keywords = ["Enhancer", "Transmuter", "Emitter", "Conjurers", "Manipulator", "Specialist"]
          found_keywords = []
          for keyword in keywords:
            if keyword in response_nen:
                found_keywords.append(keyword)

          #print response:
          print("response_intro : ",response_intro)
          print("response_nen : ",response_nen)
          print("found_keywords : ",found_keywords)
          #return:
          return jsonify({
              "response_intro": response_intro,
              "response_nen": response_nen,
              "nen_type": found_keywords[0] if found_keywords else "Enhancer"
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
