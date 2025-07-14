ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=${USER_UID}
ENV TZ=Asia/Shanghai
ENV DEBIAN_FRONTEND=noninteractive

# 自动换源为阿里云 + 安装系统依赖和常用调试工具
RUN codename=$(grep VERSION_CODENAME /etc/os-release | cut -d= -f2) && \
    echo "使用 codename: $codename" && \
    [ -f /etc/apt/sources.list ] || touch /etc/apt/sources.list && \
    rm -rf /etc/apt/sources.list.d/* && \
    echo "deb https://mirrors.aliyun.com/debian $codename main contrib non-free" > /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian-security $codename-security main" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian $codename-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian $codename-backports main contrib non-free" >> /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
        # 基础开发工具和构建依赖
        tzdata sudo git curl wget gcc g++ make build-essential \
        libffi-dev libbz2-dev zlib1g-dev libsqlite3-dev libreadline-dev \
        # 系统工具和命令行体验增强
        vim less net-tools iputils-ping bash-completion dos2unix \
        # 系统监控和分析工具
        htop ncdu \
        # 文件搜索和处理工具
        ripgrep fd-find jq \
        # 网络工具
        httpie dnsutils \
        # Python开发辅助
        python-is-python3 ipython3 \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 安装一些不在默认仓库的工具
RUN curl -fsSL https://github.com/sharkdp/bat/releases/download/v0.23.0/bat_0.23.0_amd64.deb -o bat.deb \
    && dpkg -i bat.deb \
    && rm bat.deb

# 创建非 root 用户
RUN groupadd --gid $USER_GID $USERNAME && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME && \
    echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    chown -R $USERNAME:$USERNAME /home/$USERNAME

# 切换到普通用户
USER $USERNAME
WORKDIR /home/$USERNAME

# 设置 PATH
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"

# 创建 .bashrc 并配置 PATH 和自动补全
RUN touch ~/.bashrc && \
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && \
    echo '# 启用 Bash 自动补全' >> ~/.bashrc && \
    echo 'if [ -f /etc/bash_completion ]; then' >> ~/.bashrc && \
    echo '    . /etc/bash_completion' >> ~/.bashrc && \
    echo 'fi' >> ~/.bashrc && \
    echo 'bind "set show-all-if-ambiguous on"' >> ~/.bashrc && \
    echo 'bind "set completion-ignore-case on"' >> ~/.bashrc && \
    # 配置命令别名
    echo '# 常用别名设置' >> ~/.bashrc && \
    echo 'alias ll="ls -la"' >> ~/.bashrc && \
    echo 'alias la="ls -A"' >> ~/.bashrc && \
    echo 'alias l="ls -CF"' >> ~/.bashrc && \
    echo 'alias ..="cd .."' >> ~/.bashrc && \
    echo 'alias grep="grep --color=auto"' >> ~/.bashrc && \
    # 如果安装了bat，创建cat别名
    echo 'if command -v bat &> /dev/null; then' >> ~/.bashrc && \
    echo '    alias cat="bat --style=plain"' >> ~/.bashrc && \
    echo 'fi' >> ~/.bashrc && \
    # fd-find通常安装为fdfind
    echo 'if command -v fdfind &> /dev/null; then' >> ~/.bashrc && \
    echo '    alias fd="fdfind"' >> ~/.bashrc && \
    echo 'fi' >> ~/.bashrc

# 添加登录初始化配置，确保.bashrc被加载
# 创建 .bash_profile 文件用于登录时加载 .bashrc
# 在许多系统中，登录shell会首先读取 .bash_profile 而非 .bashrc
# 这确保即使在登录时，我们定义的所有别名和环境变量也能被正确加载
RUN touch ~/.bash_profile && \
    echo 'if [ -f ~/.bashrc ]; then' >> ~/.bash_profile && \
    echo '    . ~/.bashrc' >> ~/.bash_profile && \
    echo 'fi' >> ~/.bash_profile

# 确保脚本默认有执行权限
COPY --chown=${USERNAME}:${USERNAME} scripts /tmp/scripts
RUN mkdir -p /home/${USERNAME}/scripts && \
    if [ -d /tmp/scripts ]; then \
        cp -r /tmp/scripts/* /home/${USERNAME}/scripts/ 2>/dev/null || true; \
        find /home/${USERNAME}/scripts -name "*.sh" -type f -exec chmod +x {} \; ; \
        find /home/${USERNAME}/scripts -name "*.py" -type f -exec chmod +x {} \; ; \
        # 确保所有shell脚本使用Unix行尾格式
        find /home/${USERNAME}/scripts -name "*.sh" -type f -exec dos2unix {} \; ; \
    fi

# 设置登录shell为bash
SHELL ["/bin/bash", "-c"]



