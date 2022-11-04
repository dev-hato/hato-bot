#!/usr/bin/env bash

git config user.name "github-actions[bot]"
EMAIL="41898282+github-actions[bot]@users.noreply.github.com"
git config user.email "${EMAIL}"
git commit -m "鳩は唐揚げ！(hato-botのCIを反映するよ！)"
echo "${SUDDEN_DEATH_CI_PRIVATE_KEY}" >deploy_key.pem
chmod 600 deploy_key.pem
REPO_URL="git@github.com:${ORG_NAME}/sudden-death.git"
GITHUB_HEAD="HEAD:refs/heads/pr-copy-ci"
GIT_SSH_COMMAND="ssh"
GIT_SSH_COMMAND+=" -i deploy_key.pem"
GIT_SSH_COMMAND+=" -o StrictHostKeyChecking=no"
GIT_SSH_COMMAND+=" -F /dev/null"
export GIT_SSH_COMMAND
git push -f "${REPO_URL}" "${GITHUB_HEAD}"
