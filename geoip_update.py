import os
import requests
import gzip
import shutil
import logging

# Cấu hình logger
logging.basicConfig(
    # Chọn mức độ log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',  # Định dạng log
    handlers=[
        logging.StreamHandler(),  # Ghi log ra console
        # Ghi log vào file
        logging.FileHandler(
            filename='logs/app_geoip_update.log', encoding='utf-8')
    ]
)

# URLs của các file GeoIP
url_geoip = "http://mailfud.org/geoip-legacy/GeoIP.dat.gz"
url_geoip_city = "http://mailfud.org/geoip-legacy/GeoIPCity.dat.gz"

# Đảm bảo thư mục ./dbs tồn tại
os.makedirs('./dbs', exist_ok=True)

# Hàm tải và giải nén file


def download_and_extract(url, output_path):
    # Tải file từ URL và ghi đè nếu đã tồn tại
    response = requests.get(url)
    with open(output_path + '.gz', 'wb') as f:
        f.write(response.content)

    # Giải nén file .gz và ghi đè nếu đã tồn tại
    with gzip.open(output_path + '.gz', 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    # Xóa file .gz sau khi giải nén
    # os.remove(output_path + '.gz')


# Tải và giải nén GeoIP.dat
# logging.info("Tải và giải nén './dbs/GeoIP.dat'")
# download_and_extract(url_geoip, './dbs/GeoIP.dat')

# Tải và giải nén GeoIPCity.dat
# logging.info("Tải và giải nén './dbs/GeoIPCity.dat'")
# download_and_extract(url_geoip_city, './dbs/GeoIPCity.dat')

# logging.info("Đã tải và giải nén các file thành công.")
# print("Đã tải và giải nén các file thành công.")
