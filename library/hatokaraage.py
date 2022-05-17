"""
鳩を見たらそれは唐揚げ
"""


def hato_ha_karaage(msg: str) -> str:
    """
    鳩は唐揚げだよ、美味しく食べようね
    """
    if "鳩" in msg:
        return "鳩は唐揚げ"
    return msg
