# GitHub Secrets 配置指南

## 概述

本文档详细说明了项目 CI/CD 流水线所需的 GitHub Secrets 配置。

## 必需的 Secrets

### 1. 阿里云镜像仓库凭证

用于登录阿里云容器镜像服务，推送和拉取 Docker 镜像。

#### ALIYUN_USERNAME

**描述**: 阿里云容器镜像服务的用户名

**获取方式**:
1. 登录 [阿里云容器镜像服务控制台](https://cr.console.aliyun.com/)
2. 点击右上角的「访问凭证」
3. 在「设置 Registry 登录密码」中设置或查看用户名
4. 用户名通常是您的阿里云账号

**配置步骤**:
1. 进入 GitHub 仓库的 Settings 页面
2. 在左侧菜单中选择「Secrets and variables」→「Actions」
3. 点击「New repository secret」
4. Name 输入: `ALIYUN_USERNAME`
5. Secret 输入: 您的阿里云用户名
6. 点击「Add secret」

#### ALIYUN_PASSWORD

**描述**: 阿里云容器镜像服务的密码

**获取方式**:
1. 登录 [阿里云容器镜像服务控制台](https://cr.console.aliyun.com/)
2. 点击右上角的「访问凭证」
3. 在「设置 Registry 登录密码」中设置或查看密码
4. 如果是首次使用，需要先设置密码

**配置步骤**:
1. 进入 GitHub 仓库的 Settings 页面
2. 在左侧菜单中选择「Secrets and variables」→「Actions」
3. 点击「New repository secret」
4. Name 输入: `ALIYUN_PASSWORD`
5. Secret 输入: 您的阿里云镜像仓库密码
6. 点击「Add secret」

**安全提示**:
- 不要在代码中硬编码密码
- 定期更换密码
- 使用强密码
- 限制密码的使用权限

## 可选的 Secrets

### 2. 通知 Webhook

用于接收 CI/CD 流水线的通知。

#### SLACK_WEBHOOK

**描述**: Slack 通知 Webhook URL

**获取方式**:
1. 在 Slack 中创建一个 Incoming Webhook
2. 复制 Webhook URL

**配置步骤**:
1. 进入 GitHub 仓库的 Settings 页面
2. 在左侧菜单中选择「Secrets and variables」→「Actions」
3. 点击「New repository secret」
4. Name 输入: `SLACK_WEBHOOK`
5. Secret 输入: 您的 Slack Webhook URL
6. 点击「Add secret」

#### DINGTALK_WEBHOOK

**描述**: 钉钉通知 Webhook URL

**获取方式**:
1. 在钉钉群中添加「自定义机器人」
2. 复制 Webhook URL

**配置步骤**:
1. 进入 GitHub 仓库的 Settings 页面
2. 在左侧菜单中选择「Secrets and variables」→「Actions」
3. 点击「New repository secret」
4. Name 输入: `DINGTALK_WEBHOOK`
5. Secret 输入: 您的钉钉 Webhook URL
6. 点击「Add secret」

### 3. 生产环境配置（可选）

#### SSH_PRIVATE_KEY

**描述**: 生产服务器的 SSH 私钥

**获取方式**:
1. 在生产服务器上生成 SSH 密钥对（如果还没有）
2. 复制私钥内容

**配置步骤**:
1. 进入 GitHub 仓库的 Settings 页面
2. 在左侧菜单中选择「Secrets and variables」→「Actions」
3. 点击「New repository secret」
4. Name 输入: `SSH_PRIVATE_KEY`
5. Secret 输入: 您的 SSH 私钥内容（包括 `-----BEGIN PRIVATE KEY-----` 和 `-----END PRIVATE KEY-----`）
6. 点击「Add secret**

**安全提示**:
- 只在需要部署到生产环境时配置
- 使用专用的部署密钥，不要使用个人密钥
- 在服务器上限制密钥的权限（仅允许执行部署命令）
- 定期轮换密钥

#### SSH_HOST

**描述**: 生产服务器的 IP 地址或域名

**配置步骤**:
1. 进入 GitHub 仓库的 Settings 页面
2. 在左侧菜单中选择「Secrets and variables」→「Actions」
3. 点击「New repository secret」
4. Name 输入: `SSH_HOST`
5. Secret 输入: 您的服务器 IP 或域名
6. 点击「Add secret」

#### SSH_USER

**描述**: 生产服务器的 SSH 用户名

**配置步骤**:
1. 进入 GitHub 仓库的 Settings 页面
2. 在左侧菜单中选择「Secrets and variables」→「Actions」
3. 点击「New repository secret」
4. Name 输入: `SSH_USER`
5. Secret 输入: 您的 SSH 用户名
6. 点击「Add secret」

## Secrets 配置清单

使用以下清单确保所有必需的 Secrets 都已正确配置：

- [ ] `ALIYUN_USERNAME` - 阿里云镜像仓库用户名（必需）
- [ ] `ALIYUN_PASSWORD` - 阿里云镜像仓库密码（必需）
- [ ] `SLACK_WEBHOOK` - Slack 通知 Webhook（可选）
- [ ] `DINGTALK_WEBHOOK` - 钉钉通知 Webhook（可选）
- [ ] `SSH_PRIVATE_KEY` - 生产服务器 SSH 私钥（可选，仅生产环境）
- [ ] `SSH_HOST` - 生产服务器地址（可选，仅生产环境）
- [ ] `SSH_USER` - 生产服务器用户名（可选，仅生产环境）

## 验证配置

配置完成后，可以通过以下方式验证：

### 1. 测试镜像仓库连接

创建一个测试 PR，检查 CI/CD 流水线是否能够成功登录阿里云镜像仓库。

### 2. 检查 Secrets 使用

在 GitHub Actions 的日志中，Secrets 会被自动屏蔽，不会显示明文。

### 3. 测试部署

如果配置了生产环境相关的 Secrets，可以测试手动触发生产环境部署。

## 常见问题

### Q1: 如何更新 Secret？

1. 进入 GitHub 仓库的 Settings 页面
2. 在左侧菜单中选择「Secrets and variables」→「Actions」
3. 找到要更新的 Secret
4. 点击右侧的「Update」按钮
5. 输入新的值
6. 点击「Update secret」

### Q2: Secret 会显示在日志中吗？

不会。GitHub Actions 会自动屏蔽 Secrets，不会在日志中显示明文。

### Q3: 如何删除 Secret？

1. 进入 GitHub 仓库的 Settings 页面
2. 在左侧菜单中选择「Secrets and variables」→「Actions」
3. 找到要删除的 Secret
4. 点击右侧的「Remove」按钮
5. 确认删除

### Q4: Secret 有大小限制吗？

有的，单个 Secret 的大小限制为 64 KB。

### Q5: 如何查看 Secret 的使用历史？

GitHub 不提供 Secret 的使用历史记录。建议定期轮换 Secrets。

### Q6: 阿里云镜像仓库密码忘记了怎么办？

1. 登录 [阿里云容器镜像服务控制台](https://cr.console.aliyun.com/)
2. 点击右上角的「访问凭证」
3. 在「设置 Registry 登录密码」中重置密码
4. 更新 GitHub 中的 `ALIYUN_PASSWORD` Secret

### Q7: 如何限制 Secret 的使用范围？

GitHub Actions 的 Secret 是仓库级别的，所有 workflow 都可以访问。如果需要更细粒度的控制，可以考虑：
- 使用 Environment secrets
- 使用 Organization secrets
- 使用第三方密钥管理服务（如 HashiCorp Vault）

## 最佳实践

1. **定期轮换 Secrets**: 建议每 3-6 个月更换一次密码和密钥
2. **使用强密码**: 密码长度至少 12 位，包含大小写字母、数字和特殊字符
3. **最小权限原则**: 只授予必要的权限
4. **监控使用情况**: 定期检查 GitHub Actions 的日志，确保 Secrets 被正确使用
5. **备份配置**: 保存一份 Secrets 配置清单，但不保存实际的 Secret 值
6. **使用环境变量**: 在 workflow 中使用环境变量引用 Secrets，提高可读性

## 相关文档

- [GitHub Actions Secrets 文档](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [阿里云容器镜像服务文档](https://help.aliyun.com/product/60716.html)
- [CI/CD 工作流程](./CI-CD工作流程.md)
- [容器镜像管理](./容器镜像管理.md)
