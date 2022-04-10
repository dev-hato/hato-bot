import subprocess

a = subprocess.run(
    ["yarn", "run", "textlint", "--stdin"],
    input="我々は幽霊です。\nそうだ。",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
print(a.stderr)
