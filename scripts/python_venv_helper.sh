#!/usr/bin/env bash
# vi: cc=80 spell

Usage()
{
  cat << EOF
$(basename ${0})
  Script for helping using python virtual environment.

Usage:
  -a|--active
    Shows command to activate virtual environment.
  -c|--create)
    Create python virtual environment.
  -d|--deactivate)
    Shows command to deactivate virtual environment.
  -h|--help
    Display this message.
  -i|--dependencies-install)
    Shows command to install python dependencies from \${requirements}.
  -r|--requirements)
    Set \${requirements} variable.
    By default it is \${WORKSPACE}/requirements.txt
  -s|--dependencies-save)
    Shows command to save python dependencies at file \${requirements}
  -w|--workspace
    Set working directory. If not set \$(pwd) is used.
    Other possibility is to set shell variable \${WORKSPACE}
EOF
}

Environment_create()
{
  Environment_directory_get
  python -m pip install --user virtualenv
  python -m venv ${environment_dir}
}

Environment_activate()
{
  Environment_directory_get
  echo "Run:"
  echo -e "\tsource ${environment_dir}/bin/activate"
}

Environment_dactivate()
{
  echo "Run:"
  echo -e "\tdeactivate"
}

Environment_directory_get()
{
  Workspace_get
  environment_dir=${environment_dir="${WORKSPACE}/venv"}
}

Dependencies_install()
{
  Requirements_file_name_get
  if [ ! -f ${requirements} ] ; then
    echo "File ${requirements} doesn't exists. No dependencies to install"
    exit ${ERROR}
  fi
  echo "Run:"
  echo -e "\tpython -m pip install --requirement \"${requirements}\""
}

Dependencies_save()
{
  Requirements_file_name_get
  echo "Run:"
  echo -e "\tpython -m pip freeze > ${requirements}"
}

Workspace_get()
{
  WORKSPACE=${WORKSPACE:=$(pwd)}
  echo "WORKSPACE= ${WORKSPACE}"
}

Requirements_file_name_get()
{
  Workspace_get
  requirements=${requirements:="${WORKSPACE}/requirements.txt"}
  echo "requirements=${requirements}"
}

################################################################################
# MAIN
################################################################################
ERROR=-1

if [[ $# -eq 0 ]]; then
  Usage
  exit
fi

while [[ $# -gt 0 ]]; do
  case ${1} in
    -a|--activate)
      Environment_activate
      ;;
    -c|--create)
      Environment_create
      ;;
    -d|--deactive)
      Environment_dactivate
      ;;
    -i|--dependecies-install)
      Dependencies_install
      ;;
    -r|--requirements)
      shift
      requirements="${1}"
      ;;
    -s|--dependecies-save)
      Dependencies_save
      ;;
    -h|--help)
      Usage
      exit
      ;;
    -w|--workspace)
      shift
      WORKSPACE=${1}
      ;;
    *)
      echo -e "Unknown options ${1}"
      exit
      ;;
  esac
  shift
done
