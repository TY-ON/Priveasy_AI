#!/bin/bash

# 이미지 이름이 전달되었는지 확인
if [ -z "$1" ]; then
  echo "Usage: $0 <docker-image-name>"
  exit 1
fi

IMAGE_NAME="$1"

# 실행 전에 credential.json 파일의 경로를 확인하세요.
# 예시에서는 로컬의 /path/to/credential.json 파일을 컨테이너 내부 /credentials/adc.json 경로로 마운트합니다.
# 환경변수 GOOGLE_APPLICATION_CREDENTIALS가 컨테이너 내부 경로를 가리키도록 설정합니다.
docker run -p 5001:5001 \
  -v /path/to/credential.json:/credentials/adc.json \
  -e GOOGLE_APPLICATION_CREDENTIALS=/credentials/adc.json \
  "$IMAGE_NAME"
