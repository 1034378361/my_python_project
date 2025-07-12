# 常见问题 (FAQ)

## 安装和环境

### Q: 如何安装uv?
A: 访问 [uv官方文档](https://docs.astral.sh/uv/getting-started/installation/) 获取安装指南。

### Q: 项目初始化失败怎么办?
A: 确保你已安装uv，然后在项目根目录运行 `python scripts/init.py`

### Q: 如何切换Python版本?
A: 使用uv直接指定版本: `uv venv --python 3.11` 或修改 `.python-version` 文件

## 开发相关

### Q: 如何添加新的依赖?
A: 使用 `uv add package_name` 或在 `pyproject.toml` 中添加依赖，然后运行 `uv sync`

### Q: uv和pip有什么区别?
A: uv是极速Python包管理器，比pip快10-100倍，提供更好的依赖解析和虚拟环境管理

### Q: 如何在uv环境中运行脚本?
A: 使用 `uv run python script.py` 或先激活虚拟环境再运行

### Q: 如何运行测试?
A: 使用 `make test` 或 `uv run pytest`

### Q: 代码格式化失败怎么办?
A: 运行 `make format` 自动修复大部分格式问题

### Q: 如何生成文档?
A: 运行 `make docs` 启动文档服务器

## 构建和发布

### Q: 如何构建包?
A: 运行 `make build` 或 `uv build`

### Q: 如何发布到PyPI?
A: 项目配置了GitHub Actions自动发布，创建git标签即可触发

### Q: 版本号如何管理?
A: 使用 `setuptools_scm` 基于git标签自动管理版本号

## 项目配置

### Q: 如何修改项目类型?
A: 项目类型在创建时确定，如需修改需要手动调整依赖和文件结构

### Q: 如何禁用某些功能?
A: 修改 `pyproject.toml` 中的 `optional-dependencies` 配置

如有其他问题，请在GitHub上创建Issue。