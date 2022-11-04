#!/usr/bin/env bash

file_name=Dockerfile
package_name=pipenv

if [ -f ${file_name} ]; then
  package_name_v=$(grep -oE "${package_name}[^ ]+" ${file_name})
else
  package_name_v=${package_name}
fi

pip install ${package_name_v}
