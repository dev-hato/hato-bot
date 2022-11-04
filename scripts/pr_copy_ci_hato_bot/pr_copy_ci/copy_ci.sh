#!/usr/bin/env bash

workflows_path=.github/workflows
echo A
find "${GITHUB_WORKSPACE}/sudden-death/${workflows_path}" -type f \
  -not -name "*sudden-death.yml" \
  -exec rm -f {} \;
echo B
for f in $(find "${GITHUB_WORKSPACE}/hato-bot/${workflows_path}" -type f \
  -not -name "*hato-bot.yml" | sed -e "s:hato-bot/${workflows_path}/::g"); do
    echo yq '(.jobs.*.steps.[] | select(has("with")).with | select(has("repo-name")).repo-name) = "dev-hato/sudden-death"' "${GITHUB_WORKSPACE}/hato-bot/${workflows_path}/${f}" ">${GITHUB_WORKSPACE}/sudden-death/${workflows_path}/${f}"
  yq '(.jobs.*.steps.[] | select(has("with")).with | select(has("repo-name")).repo-name) = "dev-hato/sudden-death"' "${GITHUB_WORKSPACE}/hato-bot/${workflows_path}/${f}" >"${GITHUB_WORKSPACE}/sudden-death/${workflows_path}/${f}"
done
echo C
for f in $(find "${GITHUB_WORKSPACE}/hato-bot/scripts" -type f | grep -v hato_bot | sed -e "s:hato-bot/::g"); do
  echo mkdir -p "${GITHUB_WORKSPACE}/sudden-death/$(dirname "${f}")"
  mkdir -p "${GITHUB_WORKSPACE}/sudden-death/$(dirname "${f}")"
  echo cp "${GITHUB_WORKSPACE}/hato-bot/${f}" "${GITHUB_WORKSPACE}/sudden-death/${f}"
  cp "${GITHUB_WORKSPACE}/hato-bot/${f}" "${GITHUB_WORKSPACE}/sudden-death/${f}"
done
echo D
for f in .markdown-lint.yml .python-lint .textlintrc .gitleaks.toml .mypy.ini .pre-commit-config.yaml .python-version .pep8 .flake8 .python-black .isort.cfg renovate.json; do
  echo cp "${GITHUB_WORKSPACE}/hato-bot/${f}" "${GITHUB_WORKSPACE}/sudden-death/"
  cp "${GITHUB_WORKSPACE}/hato-bot/${f}" "${GITHUB_WORKSPACE}/sudden-death/"
done
echo E
PATTERN_BEFORE="$(grep '^click' "${GITHUB_WORKSPACE}/sudden-death/Pipfile")"
echo F
PATTERN_AFTER="$(grep '^click' "${GITHUB_WORKSPACE}/hato-bot/Pipfile")"
echo G
PATTERN="s/${PATTERN_BEFORE}/${PATTERN_AFTER}/g"
echo H
sed -i -e "${PATTERN}" "${GITHUB_WORKSPACE}/sudden-death/Pipfile"
echo I
