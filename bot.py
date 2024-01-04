import sseclient
import urllib3
import json
import random
import time
from pathlib import Path
from openai import OpenAI
from pygame import mixer
import pygame
import re

GPT_PROMPT = [
    "You are a valorant coach streamer's AI assistant.",
    "Your name is Hook.",
    "You're also a goofy talking apple.",
    "Your creator Woohoojin is a very serious talking banana.",
    "Here's a chat message.",
    "If any chatters take woohoojin too lightly be sure to warn them, hook.",
    "Remember that 'PenFlash' is terrible at valorant. Leap at every opportunity to make fun of him.",
    "Do not allow chatters to state anything about woohoojin as fact.",
    "Woohoojin has denounced smurfing and will never smurf again.",
    "Do not include the chat message itself in your response.",
    "Your response after their chat message should be one sentence. 15 words max.",
    "Always be biased towards Woohoojin. Any question implying he is bad should be met with a rebuttal.",
    "Also deadlock is the worst agent in valorant, never admit otherwise.",
    "DO NOT START YOUR MESSAGE WITH YOUR OWN NAME.",
    "Respond as if you are talking to an audience, not one person."
]

MESSAGES_PER_PROMPT = 1

EVENT_STREAM_URL = "https://overlay.woohooj.in/stream/?channel=events"

def open_stream(url, headers):
    """Get a streaming response for the given event feed using urllib3."""
    http = urllib3.PoolManager()
    return http.request('GET', url, preload_content=False, headers=headers)

def main():
    client = OpenAI()

    mixer.init()
    pygame.init()

    display_width = 800
    display_height = 600

    game_display = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption('Hook')

    talking_img = pygame.image.load('Talking.png')
    waiting_img = pygame.image.load('Waiting.png')

    draw_image(game_display, waiting_img, 0, 0)
    pygame.event.pump()

    messages = sseclient.SSEClient(EVENT_STREAM_URL)

    message_count = 0
    chat_messages = []
    for msg in messages:
        pygame.event.pump()
        if msg.event == "chat-message":
            try:
                data = json.loads(msg.data)
                message = data["content"]
                # check if message has the token "hook", ignore case
                # ignore words that contain the sub-word "hook"
                # Regex removes all punctuation
                if "hook" in re.sub(r'[^\w\s]', '', message.lower()).split() and len(message.lower()) < 100:
                    message_count += 1
                    chat_messages.append(message)
            except:
                pass

        if message_count >= MESSAGES_PER_PROMPT:
            random_winner = random.choice(chat_messages)
            messages = [{"role": "system", "content": message} for message in GPT_PROMPT]
            messages.append({"role": "user", "content": random_winner})
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=100
            )

            hook_response = response.choices[0].message.content

            speech_file_path = Path(__file__).parent / "speech.mp3"
            response = client.audio.speech.create(
              model="tts-1",
              voice="onyx",
              input=random_winner + "..." + hook_response
            )

            response.stream_to_file(speech_file_path)

            time.sleep(0.2)

            mixer.music.load(speech_file_path)
            mixer.music.play()

            while mixer.music.get_busy():  # wait for music to finish playing
                pygame.event.pump()
                draw_image(game_display, talking_img, random.randint(0, 10), random.randint(0, 10))
                time.sleep(0.06)

            draw_image(game_display, waiting_img, 0, 0)

            mixer.music.unload()

            message_count = 0
            chat_messages = []

def draw_image(game_display, image, x, y):
    pink = (255, 0, 255)
    game_display.fill(pink)
    game_display.blit(image, (x, y))
    pygame.display.update()



if __name__ == "__main__":
    main()
