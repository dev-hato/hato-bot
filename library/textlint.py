# coding: utf-8

"""
textlintを使って文章校正を行う
"""

import subprocess
from typing import Optional


def get_textlint_result(text: str) -> Optional[str]:
    """textlintを使って文章校正を行う"""
    # pylint: disable=W1510
    process = subprocess.run(
        [
            "/usr/src/app/node_modules/.bin/textlint",
            "--stdin",
            "--stdin-filename=output.txt",
        ],
        input=text,
        encoding="UTF-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    for fd in [process.stderr, process.stdout]:
        res = fd.strip()
        if res:
            return "```\n" + res + "\n```"

    return None
