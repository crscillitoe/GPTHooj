import sseclient
import urllib3
import json
import random
from pathlib import Path
from openai import OpenAI
from pygame import mixer

# Opening JSON file
f = open('SECRETS.json')

# returns JSON object as
# a dictionary
loaded_file = json.load(f)
org_id = loaded_file["orgID"]

GPT_PROMPT = [
    "You are a valorant coach streamer's AI assistant.",
    "Your name is Hook.",
    "You're also a goofy talking banana.",
    "Here's a chat message.",
    "Respond in one sentence. 15 words max.",
    "Start your response with the phrase 'I think'",
    "DO NOT REPEAT THE MESSAGE YOU ARE RESPONDING TO.",
    "DO NOT START YOUR MESSAGE WITH YOUR OWN NAME.",
    "Respond as if you are talking to an audience, not one person."
]

MESSAGES_PER_PROMPT = 10

EVENT_STREAM_URL = "https://overlay.woohooj.in/stream/?channel=events"

def open_stream(url, headers):
    """Get a streaming response for the given event feed using urllib3."""
    http = urllib3.PoolManager()
    return http.request('GET', url, preload_content=False, headers=headers)

def main():
    client = OpenAI(
        organization=org_id,
    )

    messages = sseclient.SSEClient(EVENT_STREAM_URL)
    message_count = 0
    chat_messages = []
    for msg in messages:
        if msg.event == "chat-message":
            try:
                data = json.loads(msg.data)
                name = data["displayName"]
                message = data["content"]
                # check if message has the token "hook", ignore case
                # ignore words that contain the sub-word "hook"
                if "hook" in message.lower().split():
                    message_count += 1
                    chat_messages.append(message)
            except:
                pass

        if message_count >= MESSAGES_PER_PROMPT:
            print("SENDING MESSAGE")

            random_winner = random.choice(chat_messages)
            print(random_winner)
            messages = [{"role": "system", "content": message} for message in GPT_PROMPT]
            messages.append({"role": "user", "content": random_winner})
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=100
            )

            hook_response = response.choices[0].message.content
            print(hook_response)

            speech_file_path = Path(__file__).parent / "speech.mp3"
            response = client.audio.speech.create(
              model="tts-1",
              voice="onyx",
              input=hook_response
            )

            response.stream_to_file(speech_file_path)

            mixer.init()
            mixer.music.load(speech_file_path)
            mixer.music.play()
            while mixer.music.get_busy():  # wait for music to finish playing
                print("waiting.. playing audio")
                time.sleep(1)

            message_count = 0
            bulk_message = ""




if __name__ == "__main__":
    main()
