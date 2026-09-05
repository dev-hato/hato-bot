from typing import Optional

from openai import OpenAI, RateLimitError

import slackbot_settings as conf

_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _client
    client = _client

    if client is None:
        client = OpenAI(api_key=conf.OPENAI_API_KEY)
        _client = client

    return client


def chat_gpt(message: str) -> Optional[str]:
    try:
        result = _get_client().chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "あなたは鳩のbotです。自然な感じで「鳩は唐揚げ！」という文章を混ぜて発言してください。",
                },
                {"role": "user", "content": message},
            ],
        )
    except RateLimitError as e:
        if e.code == "insufficient_quota":
            return "栄養が足りなくて頭がうまく働かないっぽ......。このコマンドを使いたい場合は飼い主に相談してくれっぽ。"
        else:
            raise e

    return result.choices[0].message.content


def image_create(message: str) -> Optional[str]:
    response = _get_client().images.generate(prompt=message, n=1, size="512x512")

    if response.data is None:
        return response.data

    return response.data[0].url
