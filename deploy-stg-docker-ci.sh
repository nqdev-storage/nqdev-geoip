#! /bin/bash
# deploy-stg-docker-ci.sh

# git clone repo
# git clone https://sms.jenkins:La5xBdZL6bX5FGwh@gitlab.vihatgroup.com/vihat-sms/outsource/esms-geoip.git --branch main --recurse-submodules

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
git checkout .

# git pull
git pull --recurse-submodules

# copy env production
# cp ./.env.production ./.env

# clear log files
truncate -s 0 ./logs/*.log

# build and run docker
docker-compose up -d --build

# remove image not use
docker rmi -f $(docker images -aq)
docker system prune --force

# @REM thu dọn rác, nén dữ liệu và loại bỏ các đối tượng không còn tham chiếu từ bất kỳ nhánh nào
git gc --prune=now --aggressive

# --- THE END !!! ---
