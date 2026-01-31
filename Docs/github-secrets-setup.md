# GitHub Secrets 配置指南

本文档说明了运行 GitHub Actions 工作流所需的 GitHub Secrets 配置。

## 必需的 Secrets

### Docker 部署相关

#### ALIYUN_USERNAME
- **描述**: 阿里云容器镜像仓库用户名
- **用途**: 登录阿里云容器镜像服务
- **工作流**: `.github/workflows/docker-deploy.yml`
- **如何获取**:
  1. 访问 [阿里云容器镜像服务](https://cr.console.aliyun.com/)
  2. 登录后进入"访问凭证"页面
  3. 设置或查看固定密码
  4. 使用你的阿里云账号作为用户名

#### ALIYUN_PASSWORD
- **描述**: 阿里云容器镜像仓库密码
- **用途**: 登录阿里云容器镜像服务
- **工作流**: `.github/workflows/docker-deploy.yml`
- **如何获取**:
  1. 访问 [阿里云容器镜像服务](https://cr.console.aliyun.com/)
  2. 登录后进入"访问凭证"页面
  3. 设置固定密码
  4. 使用设置的密码

## 配置步骤

### 方法一：通过 GitHub Web 界面配置

1. 进入你的 GitHub 仓库页面
2. 点击 **Settings** 标签
3. 在左侧菜单中找到 **Secrets and variables** → **Actions**
4. 点击 **New repository secret** 按钮
5. 输入 Secret 名称（例如：`ALIYUN_USERNAME`）
6. 输入 Secret 值
7. 点击 **Add secret** 保存
8. 重复步骤 4-7 添加其他 Secrets

### 方法二：通过 GitHub CLI 配置

```bash
# 安装 GitHub CLI（如果尚未安装）
# macOS
brew install gh

# Linux
sudo apt install gh

# Windows
winget install --id GitHub.cli

# 登录 GitHub
gh auth login

# 添加 Secrets
gh secret set ALIYUN_USERNAME
gh secret set ALIYUN_PASSWORD
```

## 验证配置

配置完成后，可以通过以下方式验证：

1. **查看 Secrets 列表**:
   - 进入仓库 Settings → Secrets and variables → Actions
   - 确认所有必需的 Secrets 都已配置

2. **测试工作流**:
   - 触发一次工作流（例如推送代码到 main 分支）
   - 查看 Actions 标签页中的运行日志
   - 确认没有 Secrets 相关的错误

## 常见问题

### Q1: 工作流失败，提示 "Invalid credentials"

**原因**: Secrets 配置错误或已过期

**解决方法**:
1. 检查阿里云容器镜像服务的用户名和密码是否正确
2. 确认 Secrets 在 GitHub 中正确配置
3. 更新过期的密码

### Q2: 工作流失败，提示 "Secret not found"

**原因**: 缺少必需的 Secret

**解决方法**:
1. 按照上述步骤添加缺失的 Secret
2. 确保 Secret 名称拼写正确（区分大小写）

### Q3: 如何更新 Secret？

**方法**:
1. 进入仓库 Settings → Secrets and variables → Actions
2. 找到要更新的 Secret
3. 点击 Secret 名称
4. 点击 **Update secret**
5. 输入新值并保存

## 安全建议

1. **定期更新密码**: 建议每 3-6 个月更新一次阿里云容器镜像服务密码
2. **最小权限原则**: 确保使用的账号只有必要的权限
3. **不要在代码中硬编码**: 永远不要将密码等敏感信息提交到代码仓库
4. **使用环境变量**: 在不同环境（开发、测试、生产）使用不同的 Secrets

## 相关文档

- [GitHub Actions Secrets 文档](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [阿里云容器镜像服务文档](https://help.aliyun.com/product/60716.html)
- [GitHub Actions 工作流配置](https://docs.github.com/en/actions)