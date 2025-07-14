# 文档部署指南

本项目已配置自动文档部署到GitHub Pages。当你推送代码到远程仓库后，文档会自动构建和部署。

## 📖 启用GitHub Pages

### 1. 推送项目到GitHub
```bash
# 首次推送
git push -u origin main
```

### 2. 启用GitHub Pages
1. 访问你的GitHub仓库页面
2. 点击 **Settings** 选项卡
3. 在左侧菜单中找到 **Pages**
4. 在 **Source** 部分选择 **GitHub Actions**
5. 保存设置

### 3. 等待部署完成
- 推送到 `main` 分支后，GitHub Actions会自动运行
- 构建完成后，文档将部署到: `https://1034378361.github.io/my_python_project/`

## 🚀 自动化工作流

### 文档构建触发条件：
- ✅ 推送到 `main` 分支
- ✅ 修改 `docs/` 目录下的文件
- ✅ 修改 `mkdocs.yml` 文件
- ✅ 手动触发（workflow_dispatch）

### Pull Request 预览：
- 🔍 PR中的文档更改会触发预览构建
- 💬 构建状态会以评论形式显示在PR中
- ⚠️ 不会实际部署，只验证构建是否成功

## 📝 本地预览

在推送前，你可以在本地预览文档：

```bash
# 安装文档依赖
uv sync --extra docs

# 启动本地服务器
uv run mkdocs serve

# 或使用make命令
make docs
```

访问 http://127.0.0.1:8000 查看文档。

## 🔧 自定义配置

### 修改文档配置
编辑 `mkdocs.yml` 文件来自定义：
- 网站标题和描述
- 主题和样式
- 导航结构
- 插件和扩展

### 添加内容
在 `docs/` 目录下添加Markdown文件：
```
docs/
├── index.md          # 首页
├── user-guide/       # 用户指南
├── examples/         # 示例
├── reference/        # API参考
└── development/      # 开发文档
```

## 🎯 最佳实践

1. **保持同步** - 代码更新时同步更新文档
2. **清晰导航** - 在mkdocs.yml中维护清晰的导航结构
3. **丰富内容** - 包含示例、API文档、最佳实践
4. **定期检查** - 确保所有链接和引用都正确

## 🐛 常见问题

### 构建失败
- 检查 `mkdocs.yml` 语法是否正确
- 确保所有链接的文件都存在
- 查看GitHub Actions日志获取详细错误信息

### 页面不更新
- 清除浏览器缓存
- 等待几分钟让CDN更新
- 检查GitHub Actions是否成功运行

### 依赖问题
```bash
# 更新文档依赖
uv sync --extra docs

# 测试本地构建
uv run mkdocs build --clean --strict
```

## 🔗 相关链接

- [MkDocs官方文档](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [GitHub Pages文档](https://docs.github.com/en/pages)