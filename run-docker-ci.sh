#! /bin/bash

# lay duong dan cua thu muc dang thu thi tep script
script_directory="$(dirname $(readlink -f $0))"
echo "Thu muc cua tep script la: $script_directory"
web_directory="$script_directory"

# Kiểm tra xem thư mục là một kho lưu trữ Git
if [ -d "$web_directory/.git" ] || git -c "$web_directory" rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "Thư mục đã được clone hoặc đã được khởi tạo dự án Git."
else
  echo "Thư mục chưa được clone hoặc chưa được khởi tạo dự án Git."
fi

# cd to target folder
cd $web_directory

# discard change
# git checkout .

# git pull
# git pull --recurse-submodules

# copy file prod env
# cp prod.env ./.env

# build and deploy docker
docker-compose up -d --build

# remove image not use
# Remove all unused images, not just dangling ones
# docker rmi -f $(docker images -aq)
docker image prune --all --force

# chay lenh nay de convet file script tu unix ve dos
# dos2unix run-docker-ci.sh
