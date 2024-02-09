#!/usr/bin/env bash

file_name=Dockerfile
package_name=pipenv

if [ -f ${file_name} ]; then
	PATTERN="${package_name}[^ ]+"
	package_name_with_version=$(grep -oE "${PATTERN}" ${file_name})
else
	package_name_with_version=${package_name}
fi

pip install "${package_name_with_version}"

if [ -f ${file_name} ]; then
	new_version="$(pip list --outdated | grep pipenv || true)"
	new_version="$(echo -e "${new_version}" | awk '{print $3}')"
	if [ -n "${new_version}" ]; then
		PATTERN_BEFORE="${package_name}[^ ]+"
		PATTERN_AFTER="${package_name}==${new_version}"
		sed -i -E "s/${PATTERN_BEFORE}/${PATTERN_AFTER}/g" ${file_name}
		pip install "${package_name}==${new_version}"
		exit 1
	fi
fi
