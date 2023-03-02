import openai

import slackbot_settings as conf


def chat_gpt(message: str) -> str:
    openai.api_key = conf.OPENAI_API_KEY
    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": message}]
    )
    return result.get("choices")[0].message.content
