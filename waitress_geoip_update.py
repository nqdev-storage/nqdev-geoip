import os
import logging
from geoip_update import download_and_extract, url_geoip, url_geoip_city

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

# Đảm bảo thư mục ./dbs tồn tại
os.makedirs('./dbs', exist_ok=True)

# Tải và giải nén GeoIP.dat
logging.info("Tải và giải nén './dbs/GeoIP.dat'")
download_and_extract(url_geoip, './dbs/GeoIP.dat')

# Tải và giải nén GeoIPCity.dat
logging.info("Tải và giải nén './dbs/GeoIPCity.dat'")
download_and_extract(url_geoip_city, './dbs/GeoIPCity.dat')

logging.info("Đã tải và giải nén các file thành công.")
print("Đã tải và giải nén các file thành công.")
