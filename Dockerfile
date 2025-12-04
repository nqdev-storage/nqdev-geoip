# ✅ Sử dụng Alpine Python nhẹ, phù hợp cho môi trường production
FROM python:3.11.2-alpine3.16

# ✅ Metadata chuẩn theo OCI
LABEL maintainer="Nguyen Quy <quyit.job@gmail.com>" \
  org.opencontainers.image.authors="Nguyen Quy <quyit.job@gmail.com>" \
  org.opencontainers.image.description="Free GeoIP & GeoLite2 platform for IP geolocation lookups, updated regularly."

# ✅ Thiết lập thư mục làm việc an toàn
WORKDIR /app

# ✅ Cài đặt build dependencies tạm thời để build nhanh hơn (nếu cần compile)
#    Chỉ thêm nếu bạn dùng các gói cần build (ví dụ: psycopg2, numpy...)
# RUN apk add --no-cache --virtual .build-deps build-base libffi-dev musl-dev gcc

# ✅ Cài các dependencies
# Copy requirements.txt vào thư mục /app trong container
COPY requirements.txt /app/
# Cài đặt các dependencies từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy toàn bộ mã nguồn sau khi dependencies đã được xử lý
COPY . /app/

# Expose cổng 8000 để chạy ứng dụng Django
EXPOSE 8000

# ✅ Không cần khai báo ENV nếu settings đã định nghĩa sẵn
# ENV DJANGO_SETTINGS_MODULE=...
# ENV DJANGO_SETTINGS_MODULE=vhs_sms_tts.settings
ENV FLASK_APP=geoip_proxy.py
ENV FLASK_ENV=production

# ✅ Chạy app bằng waitress (ổn định hơn Flask built-in)
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# CMD ["python", "geoip_proxy.py"]
# CMD [ "flask", "--app", "geoip_proxy.py", "run", "--host=0.0.0.0", "--port=5000" ]
CMD ["python", "waitress_geoip_proxy.py"]
