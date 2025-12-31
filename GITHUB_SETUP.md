# GitHub 上传指南

## 步骤1: 在 GitHub 上创建仓库

1. 登录 GitHub：https://github.com
2. 点击右上角的 "+" 号，选择 "New repository"
3. 填写仓库信息：
   - **Repository name**: `allure-handle`（或你喜欢的名字）
   - **Description**: `轻量级 Allure 报告处理工具，用于 pytest 测试框架`
   - **Visibility**: Public（公开）或 Private（私有）
   - **不要**勾选 "Initialize this repository with a README"（我们已经有了）
4. 点击 "Create repository"

## 步骤2: 连接本地仓库到 GitHub

创建仓库后，GitHub 会显示仓库地址，类似：
```
https://github.com/your-username/allure-handle.git
```

在本地执行以下命令：

```bash
# 添加远程仓库（替换为你的 GitHub 用户名和仓库名）
git remote add origin https://github.com/your-username/allure-handle.git

# 或者使用 SSH（如果配置了 SSH key）
# git remote add origin git@github.com:your-username/allure-handle.git

# 推送代码
git branch -M main
git push -u origin main
```

## 步骤3: 验证上传

上传成功后，访问你的 GitHub 仓库页面，应该能看到所有文件。

## 后续更新

以后如果有代码更新：

```bash
# 添加更改
git add .

# 提交更改
git commit -m "描述你的更改"

# 推送到 GitHub
git push
```

## 发布到 PyPI（可选）

如果要将包发布到 PyPI：

```bash
# 1. 打包
python -m build

# 2. 上传到 PyPI
pip install twine
twine upload dist/*
```

## 注意事项

1. **敏感信息**：确保 `.gitignore` 中排除了敏感文件（如 `resources/config.yaml` 中的密码）
2. **README**：GitHub 会自动显示 `README.md` 文件
3. **许可证**：如果需要，可以添加 `LICENSE` 文件

