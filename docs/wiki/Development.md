# 💻 Hướng dẫn Phát triển

Tài liệu dành cho developers muốn đóng góp hoặc mở rộng **nqdev-geoip**.

## 🛠️ Thiết lập môi trường Development

### 1. Clone Repository

```bash
git clone https://github.com/nqdev-storage/nqdev-geoip.git
cd nqdev-geoip
```

### 2. Tạo Virtual Environment

```bash
# Tạo venv
python -m venv venv

# Activate
# Linux/Mac:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate
```

### 3. Cài đặt Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (nếu có)
pip install pytest pytest-cov flake8 black
```

### 4. Cấu hình Environment Variables

```bash
# Tạo file .env (không commit vào git)
cat > .env << EOF
SECRET_KEY=dev_secret_key_here
ADMIN_TOKEN=dev_admin_token_here
FLASK_APP=geoip_proxy.py
FLASK_ENV=development
FLASK_DEBUG=1
EOF

# Load environment variables
export $(cat .env | xargs)
```

### 5. Download Databases

```bash
# Tạo thư mục dbs
mkdir -p dbs logs

# Download GeoIP databases
wget -O dbs/GeoIP.dat.gz https://mailfud.org/geoip-legacy/GeoIP.dat.gz
gunzip -f dbs/GeoIP.dat.gz

wget -O dbs/GeoIPCity.dat.gz https://mailfud.org/geoip-legacy/GeoIPCity.dat.gz
gunzip -f dbs/GeoIPCity.dat.gz
```

### 6. Chạy Development Server

```bash
# Flask development server (auto-reload)
python geoip_proxy.py

# Hoặc với flask CLI
flask run --host=0.0.0.0 --port=5000 --reload
```

Server sẽ chạy tại: `http://localhost:5000`

## 📁 Cấu trúc Project

```
nqdev-geoip/
├── .github/
│   └── workflows/          # GitHub Actions workflows
│       ├── changelog.yml
│       ├── docker-publish.yml
│       ├── geoip_update.yml
│       ├── python-app-testing.yml
│       └── sync-wiki.yml
├── dbs/                    # Database files
│   ├── GeoIP.dat
│   ├── GeoIPCity.dat
│   ├── banned_ips.json
│   ├── suspicious.txt
│   └── private_cidr_config.json
├── docs/
│   └── wiki/              # Wiki documentation
│       ├── Home.md
│       ├── Installation.md
│       ├── API-Reference.md
│       ├── Architecture.md
│       ├── Security.md
│       ├── Configuration.md
│       ├── Admin-Guide.md
│       ├── Docker-Deployment.md
│       ├── Troubleshooting.md
│       └── _Sidebar.md
├── logs/                  # Application logs
│   └── app_geoip_proxy_*.log
├── routes/                # Flask blueprints
│   ├── admin/
│   │   └── ban_routes.py
│   ├── ip2location_routes.py
│   └── user_routes.py
├── tests/                 # Unit tests
│   ├── test_ip_ban.py
│   ├── test_private_cidr.py
│   └── test_user_routes.py
├── utils/                 # Utility modules
│   ├── ip_ban.py
│   ├── private_cidr.py
│   └── response_helper.py
├── config.py              # Configuration
├── geoip_proxy.py         # Main Flask application
├── geoip_update.py        # Database update utilities
├── waitress_geoip_proxy.py    # Production WSGI server
├── waitress_geoip_update.py   # Database update script
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker build configuration
├── docker-compose.yml    # Docker Compose configuration
├── .gitignore
├── CHANGELOG.md
├── CLAUDE.md             # Claude Code instructions
├── LICENSE
├── README.md
└── SECURITY.md
```

## 🧪 Testing

### Chạy Tests

```bash
# Chạy tất cả tests
pytest

# Chạy với verbose output
pytest -v

# Chạy test cụ thể
pytest tests/test_ip_ban.py
pytest tests/test_private_cidr.py

# Chạy với coverage
pytest --cov=. --cov-report=html

# Xem coverage report
open htmlcov/index.html
```

### Viết Tests

**Example: Test IP Ban**

```python
# tests/test_ip_ban.py
import pytest
from utils.ip_ban import is_ip_banned, ban_ip, unban_ip

def test_ban_ip():
    """Test banning an IP"""
    ip = "192.168.1.100"
    reason = "Test ban"
    
    # Ban IP
    result = ban_ip(ip, reason)
    assert result == True
    
    # Check if banned
    assert is_ip_banned(ip) == True
    
    # Unban IP
    result = unban_ip(ip)
    assert result == True
    assert is_ip_banned(ip) == False

def test_suspicious_request():
    """Test suspicious request detection"""
    from utils.ip_ban import is_suspicious_request
    
    # Should detect WordPress admin
    assert is_suspicious_request("/wp-admin") == True
    
    # Should detect phpMyAdmin
    assert is_suspicious_request("/phpMyAdmin") == True
    
    # Should not detect normal path
    assert is_suspicious_request("/geoip") == False
```

### Test Coverage Goals

- **Unit Tests**: 80%+ coverage
- **Integration Tests**: Key workflows
- **API Tests**: All endpoints

## 🎨 Code Style

### Python Style Guide

Tuân theo **PEP 8** với một số điều chỉnh:

```python
# Line length: 127 characters (not 79)
# Use 4 spaces for indentation
# Use double quotes for strings
# Use type hints where appropriate

def ban_ip(ip: str, reason: str = "Suspicious request") -> bool:
    """
    Add an IP to the ban list.
    
    Args:
        ip: The IP address to ban
        reason: The reason for banning
    
    Returns:
        True if successfully banned, False otherwise
    """
    # Implementation...
```

### Linting

```bash
# Flake8 - Check code style
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Black - Auto-format code (optional)
black --line-length 127 .

# isort - Sort imports (optional)
isort .
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        args: [--line-length=127]
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=127]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
EOF

# Install hooks
pre-commit install
```

## 🔧 Thêm Features Mới

### 1. Thêm Route Mới

**Bước 1**: Tạo blueprint mới

```python
# routes/my_feature_routes.py
from flask import Blueprint, request, jsonify
from utils.response_helper import okResult

my_feature_bp = Blueprint(
    name='my_feature',
    import_name=__name__,
    url_prefix='/my-feature'
)

@my_feature_bp.route('/endpoint', methods=['GET'])
def my_endpoint():
    """
    My new endpoint
    ---
    parameters:
      - name: param
        in: query
        type: string
        required: true
    responses:
      200:
        description: Success
    tags:
      - "MyFeature"
    """
    param = request.args.get('param')
    return okResult(True, "Success", {"param": param})
```

**Bước 2**: Đăng ký blueprint

```python
# geoip_proxy.py
from routes.my_feature_routes import my_feature_bp

app.register_blueprint(my_feature_bp)
```

**Bước 3**: Viết tests

```python
# tests/test_my_feature.py
def test_my_endpoint():
    # Test implementation
    pass
```

### 2. Thêm Utility Module

```python
# utils/my_utility.py
"""
My utility module description.
"""
import logging

def my_function(param: str) -> bool:
    """
    Function description.
    
    Args:
        param: Parameter description
    
    Returns:
        Return value description
    """
    try:
        # Implementation
        return True
    except Exception as e:
        logging.error(f"Error in my_function: {e}")
        return False
```

### 3. Thêm Configuration

```python
# config.py
class Config:
    # Existing configs...
    
    # New config
    MY_NEW_CONFIG = os.environ.get('MY_NEW_CONFIG', 'default_value')
```

## 🐛 Debugging

### Debug Mode

```python
# geoip_proxy.py
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True  # Enable debug mode
    )
```

### Logging

```python
import logging

# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
logging.debug("Debug message")
logging.info("Info message")
logging.warning("Warning message")
logging.error("Error message")
logging.critical("Critical message")
```

### Interactive Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use ipdb (better)
import ipdb; ipdb.set_trace()
```

### VS Code Debug Configuration

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "geoip_proxy.py",
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "1"
            },
            "args": [
                "run",
                "--no-debugger",
                "--no-reload"
            ],
            "jinja": true
        }
    ]
}
```

## 📦 Dependencies Management

### Thêm Dependency Mới

```bash
# Install package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Hoặc chỉ thêm package cụ thể
echo "package-name==1.0.0" >> requirements.txt
```

### Update Dependencies

```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### Check for Security Vulnerabilities

```bash
# Install safety
pip install safety

# Check vulnerabilities
safety check

# Check with detailed report
safety check --full-report
```

## 🐳 Docker Development

### Build Local Image

```bash
# Build image
docker build -t nqdev-geoip:dev .

# Build with no cache
docker build --no-cache -t nqdev-geoip:dev .
```

### Run Development Container

```bash
# Run with volume mounts for live reload
docker run -d \
  --name geoip-dev \
  -p 5000:5000 \
  -v $(pwd):/app \
  -v $(pwd)/dbs:/app/dbs \
  -v $(pwd)/logs:/app/logs \
  -e FLASK_ENV=development \
  -e FLASK_DEBUG=1 \
  nqdev-geoip:dev
```

### Docker Compose Development

```yaml
# docker-compose.dev.yml
services:
  geoip:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: geoip-dev
    ports:
      - "5000:5000"
    volumes:
      - .:/app
      - ./dbs:/app/dbs
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
      - PYTHONUNBUFFERED=1
    command: python geoip_proxy.py
```

```bash
# Run development stack
docker-compose -f docker-compose.dev.yml up
```

## 🔄 Git Workflow

### Branch Strategy

```
main (production)
  ↓
develop (development)
  ↓
feature/feature-name (features)
  ↓
bugfix/bug-name (bug fixes)
```

### Commit Messages

Tuân theo **Conventional Commits**:

```bash
# Format: <type>(<scope>): <subject>

# Types:
# - feat: New feature
# - fix: Bug fix
# - docs: Documentation
# - style: Code style (formatting)
# - refactor: Code refactoring
# - test: Tests
# - chore: Maintenance

# Examples:
git commit -m "feat(api): add new endpoint for IP lookup"
git commit -m "fix(ban): fix IP ban check logic"
git commit -m "docs(wiki): update API documentation"
git commit -m "test(ip_ban): add tests for ban functionality"
```

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make Changes & Commit**
   ```bash
   git add .
   git commit -m "feat: add my feature"
   ```

3. **Push to Remote**
   ```bash
   git push origin feature/my-feature
   ```

4. **Create Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Fill in description
   - Request review

5. **Code Review**
   - Address review comments
   - Update PR

6. **Merge**
   - Squash and merge (preferred)
   - Delete branch after merge

## 🚀 Release Process

### Version Numbering

Tuân theo **Semantic Versioning** (SemVer):

```
MAJOR.MINOR.PATCH

1.0.0 → 1.0.1 (patch: bug fix)
1.0.1 → 1.1.0 (minor: new feature, backward compatible)
1.1.0 → 2.0.0 (major: breaking changes)
```

### Release Steps

1. **Update Version**
   ```python
   # geoip_proxy.py
   __version__ = "1.1.0"
   ```

2. **Update CHANGELOG.md**
   ```markdown
   ## [1.1.0] - 2026-05-26
   
   ### Added
   - New feature X
   - New endpoint Y
   
   ### Fixed
   - Bug fix Z
   
   ### Changed
   - Updated dependency A
   ```

3. **Create Git Tag**
   ```bash
   git tag -a v1.1.0 -m "Release version 1.1.0"
   git push origin v1.1.0
   ```

4. **GitHub Release**
   - Go to GitHub Releases
   - Create new release
   - Select tag v1.1.0
   - Add release notes
   - Publish

5. **Docker Image**
   - GitHub Actions auto-builds and pushes
   - Verify at `ghcr.io/nqdev-storage/nqdev-geoip:1.1.0`

## 📚 Documentation

### Code Documentation

```python
def function_name(param1: str, param2: int = 0) -> bool:
    """
    Brief description of function.
    
    Detailed description if needed. Can span multiple lines.
    Explain what the function does, not how it does it.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is invalid
        IOError: When file cannot be read
    
    Example:
        >>> result = function_name("test", 5)
        >>> print(result)
        True
    """
    # Implementation
    pass
```

### API Documentation (Swagger)

```python
@app.route('/endpoint', methods=['GET'])
def endpoint():
    """
    Endpoint description
    ---
    parameters:
      - name: param
        in: query
        type: string
        required: true
        description: Parameter description
    responses:
      200:
        description: Success response
        schema:
          type: object
          properties:
            result:
              type: string
      400:
        description: Bad request
    tags:
      - "Category"
    """
    pass
```

### Wiki Documentation

Cập nhật wiki trong `docs/wiki/`:

- **Home.md**: Trang chủ
- **Installation.md**: Hướng dẫn cài đặt
- **API-Reference.md**: Tài liệu API
- **Architecture.md**: Kiến trúc hệ thống
- **Security.md**: Bảo mật
- **Development.md**: Hướng dẫn phát triển

## 🤝 Contributing Guidelines

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person

### Contribution Checklist

- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commit messages follow convention
- [ ] PR description is clear
- [ ] All tests pass
- [ ] No linting errors

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/nqdev-storage/nqdev-geoip/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nqdev-storage/nqdev-geoip/discussions)
- **Email**: quyit.job@gmail.com

---

➡️ **Tiếp theo**: [API Reference](API-Reference) - Tài liệu API đầy đủ
