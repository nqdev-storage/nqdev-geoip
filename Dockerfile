# Sử dụng image base là Python
FROM python:3.11.2-alpine3.16

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Copy requirements.txt vào thư mục /app trong container
COPY requirements.txt /app/

# Cài đặt các dependencies từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ nội dung dự án vào thư mục /app trong container
COPY . /app/

# Expose cổng 8000 để chạy ứng dụng Django
EXPOSE 8000

# Thiết lập environment variable cho Django
# ENV DJANGO_SETTINGS_MODULE=myproject.settings
# ENV DJANGO_SETTINGS_MODULE=vhs_sms_tts.settings

# Khởi chạy ứng dụng Django
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["python", "geoip_proxy.py"]
