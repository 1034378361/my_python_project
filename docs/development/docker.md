# Docker支持

本项目提供完整的Docker支持，可以方便地将应用程序容器化部署。

## 快速开始

最简单的方法是使用`docker-compose`:

```bash
# 构建并启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止容器
docker-compose down
```

## 手动构建和运行

项目提供了便捷的脚本来构建和运行Docker容器：

```bash
# 构建Docker镜像
./scripts/docker-build.sh [标签]

# 运行Docker容器
./scripts/docker-run.sh [标签] [额外参数]
```

示例：
```bash
# 构建标签为1.0.0的镜像
./scripts/docker-build.sh 1.0.0

# 运行并传递参数
./scripts/docker-run.sh latest --config /app/config/production.yml
```

## Dockerfile说明

项目使用多阶段构建来创建精简的Docker镜像：

1. **构建阶段**：安装所有依赖并构建wheel包
2. **运行阶段**：仅安装最小化依赖，减小镜像体积

关键特性：
- 使用非root用户运行应用，提高安全性
- 优化了层缓存，加快构建速度
- 通过卷映射支持外部数据和配置

## 自定义配置

### 配置文件
将配置文件放在本地的`./config`目录，它会被映射到容器的`/app/config`目录。

### 数据持久化
容器中的`/app/data`目录被映射到本地的`./data`目录，用于存储持久化数据。

## Docker Compose

`docker-compose.yml`文件包含了应用程序的完整定义：

```yaml
services:
  app:
    build: .
    volumes:
      - ./data:/app/data
      - ./config:/app/config
```

可以根据需要自定义此文件，例如添加数据库、缓存服务等。

## 生产环境部署

对于生产环境，建议：

1. 使用特定版本标签而非`latest`
2. 设置适当的资源限制
3. 配置健康检查
4. 使用Docker Swarm或Kubernetes进行编排

例如：
```bash
docker run -d --restart=unless-stopped \
  --memory=1g --cpus=1 \
  -v /path/to/data:/app/data \
  -v /path/to/config:/app/config \
  my_python_project:1.0.0
```
