"""
textlintを使って文章校正を行う
"""

import subprocess


def get_textlint_result(text: str) -> str | None:
    """textlintを使って文章校正を行う"""
    process = subprocess.run(
        [
            "/usr/src/app/node_modules/.bin/textlint",
            "--stdin",
            "--stdin-filename=output.txt",
        ],
        input=text,
        encoding="UTF-8",
        capture_output=True,
        check=False,
    )
    for fd in [process.stderr, process.stdout]:
        res = fd.strip()
        if res:
            return "```\n" + res + "\n```"

    return None
