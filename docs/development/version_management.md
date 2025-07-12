# 版本管理指南

本项目采用基于Git标签的自动版本管理，使用`setuptools_scm`实现版本号的自动获取和管理。

## 🎯 版本管理原理

### 工作流程

1. **开发阶段**：setuptools_scm从Git标签和提交生成版本号
2. **构建阶段**：版本号自动写入包元数据和`_version.py`文件
3. **安装阶段**：用户安装的包显示正确的版本号

### 版本获取优先级

项目使用多级fallback机制确保版本号的正确性：

```
1. 包元数据 (安装后)
   ↓
2. _version.py文件 (开发环境)  
   ↓
3. fallback版本 (兜底)
```

## 📋 版本发布流程

### 标准发布流程

```bash
# 1. 确保代码已提交并测试通过
git add .
git commit -m "feat: 添加新功能"

# 2. 创建版本标签（遵循语义化版本）
git tag v1.2.0

# 3. 推送代码和标签
git push origin main
git push origin v1.2.0
```

### 自动化流程

推送标签后，GitHub Actions会自动：

1. ✅ 验证版本号
2. 🔨 构建包
3. 🧪 运行测试
4. 📦 发布到PyPI
5. 📝 创建GitHub Release

## 🏷️ 版本号规范

### 语义化版本控制

遵循[SemVer](https://semver.org/)规范：

- `v1.0.0` - 主版本.次版本.修订版本
- `v1.1.0` - 新增功能，向后兼容
- `v1.0.1` - 问题修复，向后兼容
- `v2.0.0` - 重大更改，可能不向后兼容

### 预发布版本

```bash
# 开发版本
git tag v1.0.0-dev
git tag v1.0.0-alpha.1
git tag v1.0.0-beta.1
git tag v1.0.0-rc.1
```

## 🔧 配置说明

### pyproject.toml配置

```toml
[project]
name = "your-package"
dynamic = ["version"]  # 版本号由setuptools_scm管理

[build-system]
requires = ["setuptools>=61.0", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[tool.setuptools_scm]
write_to = "src/your_package/_version.py"
version_scheme = "python-simplified-semver"
local_scheme = "no-local-version"
```

### 关键配置说明

- `dynamic = ["version"]`: 告诉setuptools版本号是动态的
- `write_to`: 指定生成版本文件的位置
- `version_scheme`: 使用简化的语义化版本方案
- `local_scheme = "no-local-version"`: 避免开发版本后缀
- `fallback_version`: 无法获取Git版本时的默认版本

## 📁 文件结构

```
your_package/
├── src/your_package/
│   ├── __init__.py          # 包含版本获取逻辑
│   └── _version.py          # setuptools_scm生成（.gitignore中）
├── pyproject.toml           # 版本管理配置
└── .gitignore              # 忽略生成的版本文件
```

## 🐛 常见问题解决

### 问题1：版本号显示不正确

**症状**：导入的包版本号与Git标签不符

**排查步骤**：

```bash
# 1. 检查setuptools_scm识别的版本
python -c "from setuptools_scm import get_version; print('SCM:', get_version())"

# 2. 检查包导入的版本
python -c "import your_package; print('Package:', your_package.__version__)"

# 3. 检查Git标签
git tag --contains HEAD
```

**解决方案**：

```bash
# 确保Git历史完整
git fetch --unshallow

# 重新安装包
pip install -e .
```

### 问题2：CI/CD版本号自动增加

**症状**：构建时版本号变成`4.0.2.dev0`等

**原因**：
- Git仓库状态不干净
- 同一提交有多个标签
- CI环境缺少Git历史

**解决方案**：

```bash
# 检查并清理多余标签
git tag --contains HEAD
git tag -d unwanted-tag
git push origin :refs/tags/unwanted-tag

# CI配置确保获取完整历史
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # 关键配置
```

### 问题3：开发环境版本号错误

**症状**：开发环境中版本号不是期望的值

**解决方案**：

```bash
# 方法1：创建开发标签
git tag v1.0.0-dev

# 方法2：设置环境变量
export VERSION=1.0.0-dev

# 方法3：重新生成版本文件
rm src/your_package/_version.py
python -c "from setuptools_scm import get_version; print(get_version())"
```

## 🧪 验证测试

### 本地验证

```bash
# 1. 版本检查
python -c "from setuptools_scm import get_version; print('SCM Version:', get_version())"
python -c "import your_package; print('Package Version:', your_package.__version__)"

# 2. 构建测试
python -m build
ls dist/

# 3. 安装测试
pip install dist/*.whl
python -c "import your_package; print('Installed:', your_package.__version__)"
```

### CI/CD验证

检查GitHub Actions日志：

1. ✅ "验证版本号"步骤显示正确版本
2. ✅ 构建的文件名包含正确版本
3. ✅ 发布到PyPI的版本号正确

## 📚 版本历史管理

### 自动生成CHANGELOG

项目集成了自动CHANGELOG生成：

```bash
# 手动生成
make changelog

# 自动生成（通过GitHub Actions）
git push origin main  # 推送到主分支时自动生成
```

### 版本标签管理

```bash
# 查看所有标签
git tag

# 查看标签详情
git show v1.0.0

# 删除本地标签
git tag -d v1.0.0

# 删除远程标签
git push origin :refs/tags/v1.0.0
```

## 🎨 最佳实践

### DO（推荐做法）

✅ 使用语义化版本号（v1.2.3）  
✅ 每个版本只创建一个标签  
✅ 标签使用v前缀（v1.0.0）  
✅ 在CI中使用`fetch-depth: 0`  
✅ 定期清理无用标签  

### DON'T（避免做法）

❌ 手动修改版本号  
❌ 在同一提交创建多个标签  
❌ 修改已发布的标签  
❌ 在.gitignore中提交_version.py  
❌ 跳过版本号验证步骤  

## 🔍 调试技巧

### 启用详细日志

```bash
# 查看setuptools_scm详细信息
SETUPTOOLS_SCM_DEBUG=1 python -c "from setuptools_scm import get_version; print(get_version())"

# 查看Git状态
git status
git log --oneline -10
git describe --tags
```

### 常用调试命令

```bash
# 检查版本配置
python -c "import toml; print(toml.load('pyproject.toml')['tool']['setuptools_scm'])"

# 测试版本获取
python -c "
try:
    from setuptools_scm import get_version
    print('SCM Version:', get_version())
except Exception as e:
    print('Error:', e)
"

# 检查包安装状态
pip show your-package
```

---

## 💡 总结

这套版本管理方案的核心优势：

1. **自动化**：版本号完全由Git标签驱动
2. **一致性**：开发、构建、安装各环节版本号保持一致
3. **健壮性**：多级fallback机制确保可靠性
4. **简洁性**：避免复杂的版本管理脚本

遵循本指南，您可以实现"一次配置，永久有效"的版本管理体验。