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
