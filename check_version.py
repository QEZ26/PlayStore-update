name: Check Play Store Update

on:
  schedule:
    # 每天北京时间早上 9 点和晚上 9 点各自动检查一次
    - cron: '0 1,13 * * *'
  workflow_dispatch: # 允许你手动点击按钮触发运行

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install requests beautifulsoup4

    - name: Run checker
      env:
        TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
        TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
      run: python check_version.py

    - name: Commit and push if version changed
      run: |
        git config --global user.name "VersionBot"
        git config --global user.email "bot@github.com"
        git add last_version.txt || true
        git commit -m "Update last version stamp" || true
        git push || true

