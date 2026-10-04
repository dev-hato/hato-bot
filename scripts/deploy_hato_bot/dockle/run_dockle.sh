#!/usr/bin/env bash
set -euo pipefail

repository="${REPOSITORY:-dev-hato/hato-bot}"
export TAG_NAME="${HEAD_REF//\//-}"
dockle_version="$(cat .dockle-version)"
curl -L -o dockle.deb "https://github.com/goodwithtech/dockle/releases/download/v${dockle_version}/dockle_${dockle_version}_Linux-64bit.deb"
sudo dpkg -i dockle.deb
images=(
	"ghcr.io/${repository}/postgres:${TAG_NAME}"
	"ghcr.io/${repository}/hato-bot:${TAG_NAME}"
)

for image_name in "${images[@]}"; do
	docker pull "${image_name}"
done

for image_name in "${images[@]}"; do
	cmd="dockle --exit-code 1 "

	if [[ "${image_name}" =~ "postgres" ]]; then
		cmd+="-ak key "
	elif [[ "${image_name}" =~ "hato-bot" ]]; then
		cmd+="-i CIS-DI-0006 -i DKL-DI-0005 -af settings.py "
	fi

	cmd+="${image_name}"
	echo "> ${cmd}"
	eval "${cmd}"
done
