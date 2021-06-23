import os
import subprocess
from typing import Optional

def get_textlint_result(text: str) -> Optional[str]:
    process = subprocess.run(['node_modules/.bin/textlint', '--stdin'],
                             input=text, encoding='UTF-8', stdout=subprocess.PIPE)

    if process.stderr is not None:
        return process.stderr

    is_start_output = False
    res = list()

    for line in process.stdout.split(os.linesep):
        line = line.strip()
        if is_start_output:
            res.append(line)
        elif line == '<text>':
            is_start_output = True

    res = os.linesep.join(res).strip()

    if res:
        return '```'+res+'```'

    return None
