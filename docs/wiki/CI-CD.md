# 🔄 CI/CD Pipeline

Tài liệu về hệ thống CI/CD tự động của **nqdev-geoip**.

## 📋 Tổng quan

**nqdev-geoip** sử dụng **GitHub Actions** để tự động hóa:

- ✅ Testing & Linting
- ✅ Database Updates (Weekly)
- ✅ Docker Image Build & Publish
- ✅ Changelog Generation
- ✅ Wiki Synchronization

## 🔧 GitHub Actions Workflows

### 1. Python App Testing

**File**: `.github/workflows/python-app-testing.yml`

**Trigger**:
- Push to `main` branch
- Pull requests to `main`

**Jobs**:

```yaml
name: Python App Flask CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python 3.13
      uses: actions/setup-python@v4
      with:
        python-version: "3.13"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8 pytest
        pip install -r requirements.txt
    
    - name: Lint with flake8
      run: |
        # Stop on syntax errors or undefined names
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        # Exit-zero treats all errors as warnings
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Test with pytest
      run: |
        pytest
```

**Mục đích**:
- Đảm bảo code quality
- Chạy unit tests
- Phát hiện lỗi sớm

### 2. GeoIP Database Update

**File**: `.github/workflows/geoip_update.yml`

**Trigger**:
- Schedule: Mỗi Chủ Nhật lúc 00:00 UTC
- Manual trigger (workflow_dispatch)
- Repository dispatch

**Jobs**:

```yaml
name: Update GeoIP Databases

on:
  schedule:
    - cron: "0 0 * * 0"  # Every Sunday at 00:00 UTC
  workflow_dispatch:
  repository_dispatch:

permissions:
  contents: write

jobs:
  update_geoip:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v2
      with:
        token: ${{ secrets.GH_TOKEN }}
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.13"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests
        pip install -r requirements.txt
    
    - name: Run waitress_geoip_update.py
      run: |
        python waitress_geoip_update.py
    
    - name: Configure Git
      run: |
        git config --global user.name "github-actions"
        git config --global user.email "github-actions@github.com"
    
    - name: Commit and push dbs folder
      run: |
        VERSION=$(date +"%Y-%m-%d")
        git add ./dbs
        if git diff --cached --quiet; then
            echo "No changes to commit."
        else
            git commit -m "Update GeoIP databases - v$VERSION"
            git push origin main
        fi
```

**Mục đích**:
- Tự động cập nhật GeoIP databases hàng tuần
- Đảm bảo dữ liệu luôn mới nhất
- Commit và push changes tự động

**Database Sources**:
- GeoIP.dat: https://mailfud.org/geoip-legacy/GeoIP.dat.gz
- GeoIPCity.dat: https://mailfud.org/geoip-legacy/GeoIPCity.dat.gz

### 3. Docker Image Build & Publish

**File**: `.github/workflows/docker-publish.yml`

**Trigger**:
- Push to `main` branch
- New tags (v*)
- Manual trigger

**Jobs**:

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v2
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=sha
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
```

**Mục đích**:
- Build Docker image tự động
- Push to GitHub Container Registry (ghcr.io)
- Tag images với version và SHA

**Image Tags**:
- `latest`: Latest main branch
- `v1.0.0`: Semantic version tags
- `sha-abc123`: Git commit SHA

### 4. Changelog Generation

**File**: `.github/workflows/changelog.yml`

**Trigger**:
- New release published

**Jobs**:

```yaml
name: Generate Changelog

on:
  release:
    types: [published]

jobs:
  changelog:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v2
      with:
        fetch-depth: 0
    
    - name: Generate changelog
      uses: orhun/git-cliff-action@v2
      with:
        config: cliff.toml
        args: --verbose
      env:
        OUTPUT: CHANGELOG.md
    
    - name: Commit changelog
      run: |
        git config user.name "github-actions"
        git config user.email "github-actions@github.com"
        git add CHANGELOG.md
        git commit -m "docs: update CHANGELOG.md for ${{ github.event.release.tag_name }}"
        git push
```

**Mục đích**:
- Tự động tạo CHANGELOG.md
- Cập nhật khi có release mới

### 5. Wiki Synchronization

**File**: `.github/workflows/sync-wiki.yml`

**Trigger**:
- Push to `main` branch (changes in docs/wiki/)
- Manual trigger

**Jobs**:

```yaml
name: Sync Wiki

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/wiki/**'
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v2
    
    - name: Sync to Wiki
      uses: SwiftDocOrg/github-wiki-publish-action@v1
      with:
        path: docs/wiki
      env:
        GH_PERSONAL_ACCESS_TOKEN: ${{ secrets.GH_TOKEN }}
```

**Mục đích**:
- Đồng bộ docs/wiki/ với GitHub Wiki
- Tự động cập nhật documentation

## 🔐 Secrets Configuration

### Required Secrets

Cấu hình trong **Settings → Secrets and variables → Actions**:

| Secret | Mô tả | Sử dụng |
|--------|-------|---------|
| `GH_TOKEN` | Personal Access Token | Push commits, sync wiki |
| `GITHUB_TOKEN` | Auto-generated | Docker registry, API access |

### Tạo Personal Access Token

1. Go to **Settings → Developer settings → Personal access tokens**
2. Click **Generate new token (classic)**
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `write:packages` (Upload packages to GitHub Package Registry)
4. Generate token
5. Copy và lưu token
6. Add to repository secrets as `GH_TOKEN`

## 📊 Workflow Status Badges

### Thêm vào README.md

```markdown
[![Python App Flask CI](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/python-app-testing.yml/badge.svg)](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/python-app-testing.yml)

[![Update GeoIP Databases](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/geoip_update.yml/badge.svg)](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/geoip_update.yml)

[![Build and Push Docker Image](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/docker-publish.yml)
```

## 🚀 Deployment Pipeline

### Automatic Deployment Flow

```
Code Push to main
    ↓
GitHub Actions Triggered
    ↓
┌─────────────────────────────────┐
│  1. Testing & Linting           │
│     - Run pytest                │
│     - Run flake8                │
│     - Check code quality        │
└──────────────┬──────────────────┘
               ↓ (if pass)
┌─────────────────────────────────┐
│  2. Docker Build                │
│     - Build image               │
│     - Tag with version          │
│     - Push to GHCR              │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│  3. Deploy (Manual/Auto)        │
│     - Pull new image            │
│     - Restart containers        │
│     - Health check              │
└─────────────────────────────────┘
```

### Weekly Database Update Flow

```
Sunday 00:00 UTC (Cron Trigger)
    ↓
GitHub Actions Triggered
    ↓
┌─────────────────────────────────┐
│  1. Download Databases          │
│     - GeoIP.dat.gz              │
│     - GeoIPCity.dat.gz          │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│  2. Extract Files               │
│     - Gunzip databases          │
│     - Verify integrity          │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│  3. Commit & Push               │
│     - git add dbs/              │
│     - git commit                │
│     - git push origin main      │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│  4. Trigger Docker Build        │
│     - New commit triggers build │
│     - New image with updated DB │
└─────────────────────────────────┘
```

## 🛠️ Manual Workflow Triggers

### Trigger via GitHub UI

1. Go to **Actions** tab
2. Select workflow
3. Click **Run workflow**
4. Select branch
5. Click **Run workflow** button

### Trigger via GitHub CLI

```bash
# Install GitHub CLI
# https://cli.github.com/

# Trigger workflow
gh workflow run geoip_update.yml

# Trigger with specific branch
gh workflow run docker-publish.yml --ref main

# List workflow runs
gh run list --workflow=python-app-testing.yml

# View workflow run details
gh run view <run-id>

# Watch workflow run
gh run watch <run-id>
```

### Trigger via API

```bash
# Trigger workflow via REST API
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/repos/nqdev-storage/nqdev-geoip/actions/workflows/geoip_update.yml/dispatches \
  -d '{"ref":"main"}'
```

## 📈 Monitoring Workflows

### View Workflow Runs

```bash
# List recent runs
gh run list --limit 10

# View specific run
gh run view <run-id>

# View logs
gh run view <run-id> --log

# Download logs
gh run download <run-id>
```

### Workflow Notifications

**Email Notifications**:
- Automatic for workflow failures
- Configure in GitHub Settings → Notifications

**Slack Integration**:
```yaml
# Add to workflow
- name: Slack Notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Workflow ${{ github.workflow }} completed'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
  if: always()
```

## 🔍 Debugging Workflows

### Enable Debug Logging

1. Go to **Settings → Secrets**
2. Add secret: `ACTIONS_STEP_DEBUG` = `true`
3. Re-run workflow

### View Detailed Logs

```bash
# Download logs
gh run download <run-id>

# View specific job logs
gh run view <run-id> --log --job <job-id>
```

### Common Issues

**Issue 1: Permission Denied**
```yaml
# Solution: Add permissions
permissions:
  contents: write
  packages: write
```

**Issue 2: Token Expired**
```bash
# Solution: Regenerate GH_TOKEN
# Update in repository secrets
```

**Issue 3: Workflow Not Triggering**
```yaml
# Check trigger conditions
on:
  push:
    branches: [ main ]
    paths:
      - '**.py'  # Only trigger on Python file changes
```

## 📋 Best Practices

### 1. Workflow Organization

```
.github/
└── workflows/
    ├── ci.yml              # Continuous Integration
    ├── cd.yml              # Continuous Deployment
    ├── scheduled.yml       # Scheduled jobs
    └── manual.yml          # Manual workflows
```

### 2. Caching Dependencies

```yaml
- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

### 3. Matrix Testing

```yaml
strategy:
  matrix:
    python-version: [3.9, 3.10, 3.11, 3.13]
    os: [ubuntu-latest, windows-latest, macos-latest]

steps:
- uses: actions/setup-python@v4
  with:
    python-version: ${{ matrix.python-version }}
```

### 4. Conditional Steps

```yaml
- name: Deploy to production
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  run: ./deploy.sh
```

### 5. Reusable Workflows

```yaml
# .github/workflows/reusable-test.yml
on:
  workflow_call:
    inputs:
      python-version:
        required: true
        type: string

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ inputs.python-version }}
```

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: '3.13'
```

## 🔄 Continuous Deployment

### Auto-deploy on Tag

```yaml
name: Deploy on Tag

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to production
      run: |
        # SSH to server
        ssh user@server << 'EOF'
          cd /app/nqdev-geoip
          git pull origin main
          docker-compose pull
          docker-compose up -d
        EOF
```

### Blue-Green Deployment

```bash
# Deploy new version (green)
docker-compose -f docker-compose.green.yml up -d

# Health check
curl -f http://localhost:5001/health || exit 1

# Switch traffic (update nginx)
# Stop old version (blue)
docker-compose -f docker-compose.blue.yml down
```

## 📊 Metrics & Analytics

### Workflow Duration

```bash
# Get workflow run duration
gh run view <run-id> --json conclusion,createdAt,updatedAt
```

### Success Rate

```bash
# Get last 100 runs
gh run list --limit 100 --json conclusion

# Calculate success rate
gh run list --limit 100 --json conclusion | \
  jq '[.[] | select(.conclusion=="success")] | length'
```

---

➡️ **Tiếp theo**: [Development](Development) - Hướng dẫn phát triển
