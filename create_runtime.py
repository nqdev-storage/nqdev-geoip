import sys

# Lấy phiên bản Python hiện tại
# Lấy chỉ phần phiên bản (ví dụ: '3.10.4')
python_version = sys.version.split()[0]

# Tạo và ghi vào file runtime.txt
with open('runtime.txt', 'w') as file:
    file.write(f'python-{python_version}')

# Đọc nội dung của file runtime.txt
with open('runtime.txt', 'r') as file:
    # In nội dung của file
    print(file.read())
