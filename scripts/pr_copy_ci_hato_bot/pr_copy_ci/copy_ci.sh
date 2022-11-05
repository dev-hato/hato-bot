#!/usr/bin/env bash

workflows_path=.github/workflows
find sudden-death/${workflows_path} -type f \
  -not -name "*sudden-death.yml" \
  -exec rm -f {} \;

for f in $(find hato-bot/${workflows_path} -type f \
  -not -name "*hato-bot.yml" | sed -e "s:hato-bot/${workflows_path}/::g"); do
  yq '(.jobs.*.steps.[] | select(has("with")).with | select(has("repo-name")).repo-name) = "dev-hato/sudden-death"' "hato-bot/${workflows_path}/${f}" >"sudden-death/${workflows_path}/${f}"
done

for f in $(find hato-bot/scripts -type f | grep -v hato_bot | sed -e "s:hato-bot/::g"); do
  mkdir -p "sudden-death/$(dirname "${f}")"
  cp "hato-bot/${f}" "sudden-death/${f}"
done

for f in .markdown-lint.yml .python-lint .textlintrc .gitleaks.toml .mypy.ini .pre-commit-config.yaml .python-version .pep8 .flake8 .python-black .isort.cfg renovate.json; do
  cp hato-bot/${f} sudden-death/
done
PATTERN_BEFORE="$(grep '^click' sudden-death/Pipfile)"
PATTERN_AFTER="$(grep '^click' hato-bot/Pipfile)"
PATTERN="s/${PATTERN_BEFORE}/${PATTERN_AFTER}/g"
sed -i -e "${PATTERN}" sudden-death/Pipfile
