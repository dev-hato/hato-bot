import openai

import slackbot_settings as conf


def chat_gpt(message: str) -> str:
    openai.api_key = conf.OPENAI_API_KEY
    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[
            {"role": "system", "content": "自然な感じで「鳩は唐揚げ！」という文章を混ぜて発言してください。"},
            {"role": "user", "content": message}
        ]
    )
    return result.get("choices")[0].message.content
