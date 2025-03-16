#!/bin/bash

source /scripts/logging.sh

BASE_COMMAND=main:app
BASE_FLAGS=(
  "--host=0.0.0.0"
  "--port=8000"
  "--use-colors"
)
DEV_FLAGS=(
  "--reload"
)


start() {
  if [[ "$ENV_STATE" == "production" || "$ENV_STATE" == "staging" ]]; then
    log_message INFO "Starting service in ${GREEN}$ENV_STATE mode${NO_COLOR}..."
    uvicorn "$BASE_COMMAND" "${BASE_FLAGS[@]}"
  else
    log_message WARNING "Starting service in ${YELLOW}development mode${NO_COLOR}..."
    uvicorn "$BASE_COMMAND" "${BASE_FLAGS[@]}" "${DEV_FLAGS[@]}"
  fi
}

start
