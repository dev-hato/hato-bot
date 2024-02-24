"""
hato-bot用のおみくじラッパー
"""

from enum import Enum, auto

from library.omikuji import OmikujiResult, OmikujiResults, draw


class HatoMikuji:
    """
    HatoMikuji

    Omikujiをhato-bot用に設定を導入しラップするAdapter
    """

    class OmikujiEnum(Enum):
        """
        HatoMikuji用のおみくじ結果一覧
        """

        DAI_KICHI = auto()
        CHU_KICHI = auto()
        SHO_KICHI = auto()
        KICHI = auto()
        SUE_KICHI = auto()
        AGE_KICHI = auto()
        KYO = auto()
        DAI_KYO = auto()

    # メンテナンス性のために排出率をパーミルに正規化(合計1000)すること
    OMIKUJI_CONFIG = OmikujiResults(
        {
            OmikujiEnum.DAI_KICHI: OmikujiResult(
                15, ":tada: 大吉 何でもうまくいく!!気がする!!"
            ),
            OmikujiEnum.KICHI: OmikujiResult(100, ":smirk: 吉 まあうまくいくかも!?"),
            OmikujiEnum.CHU_KICHI: OmikujiResult(
                300, ":smile: 中吉 そこそこうまくいくかも!?"
            ),
            OmikujiEnum.SHO_KICHI: OmikujiResult(
                330, ":smiley: 小吉 なんとなくうまくいくかも!?"
            ),
            OmikujiEnum.SUE_KICHI: OmikujiResult(
                165, ":expressionless: 末吉 まあ多分うまくいくかもね……!?"
            ),
            OmikujiEnum.AGE_KICHI: OmikujiResult(
                160, ":poultry_leg: 揚げ吉 鳩を揚げると良いことあるよ!!"
            ),
            OmikujiEnum.KYO: OmikujiResult(
                28, ":cry: 凶 ちょっと慎重にいったほうがいいかも……"
            ),
            OmikujiEnum.DAI_KYO: OmikujiResult(
                2, ":crying_cat_face: 大凶 そういう時もあります……猫になって耐えましょう"
            ),
        }
    )

    @classmethod
    def draw(cls):
        return draw(cls.OMIKUJI_CONFIG)[1].message
