<<<<<<< HEAD:packages/backend/scraper/Dockerfile
# 使用官方 Python slim 基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 更新包索引，并安装 wget、gnupg 和 unzip 等工具
RUN apt-get update && apt-get install -y wget gnupg unzip

# 添加 Google 的 GPG key 并添加 Chrome 仓库（注意：这里要求基础镜像为 amd64 架构，如非则需要调整）
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# 下载并安装与 Chrome 匹配的 ChromeDriver（linux64）
RUN CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -O /tmp/chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver_linux64.zip && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件（假设你有 requirements.txt，列出所有需要的 Python 库）
COPY requirements.txt ./

# 安装 Python 相关依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制爬虫代码到容器
COPY . .

# 赋予启动脚本执行权限（尽管挂载可能会覆盖这些权限，最好保证宿主机也设置了正确权限）
RUN chmod +x ./start_crawler.sh

# 设置容器启动时运行爬虫启动脚本
CMD ["./start_crawler.sh"]
=======
FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    echo "Detected Chrome version: $CHROME_VERSION" && \
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    chromedriver --version && \
    rm -rf chromedriver-linux64.zip chromedriver-linux64

# Set up working directory
WORKDIR /app/scraper

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install python-dotenv

# Copy scraper files
COPY *.py ./
COPY *.sh ./
RUN chmod +x *.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set up entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
>>>>>>> cae1bf3a9eeb8d52eb59b903c7730d70f2c20cdd:packages/scraper/Dockerfile
