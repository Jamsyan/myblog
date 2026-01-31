# CI/CD 工作流程说明

## 概述

本项目采用**中央调度器**模式的 CI/CD 流水线，通过单一入口点智能调度各个子工作流，避免通知轰炸，优化资源使用。流水线集成阿里云容器镜像服务，支持多环境部署和自动回滚。

## 核心优势

### 🎯 中央调度器模式
- **单一入口**: 所有触发事件统一由中央调度器处理
- **智能调度**: 根据触发条件自动决策执行哪些检查项
- **统一通知**: 一次提交只发送一封汇总通知，避免通知轰炸
- **资源优化**: 减少重复执行，节省 GitHub Actions 配额

## 架构设计

```
代码提交 / PR 创建 / 手动触发
    ↓
┌─────────────────────────────────────────────────────────────┐
│              🎯 中央调度器 (ci-scheduler)                  │
│  - 接收所有触发事件                                       │
│  - 智能决策执行哪些检查                                   │
│  - 调度子工作流                                           │
│  - 收集执行结果                                           │
│  - 统一发送通知                                           │
└─────────────────────────────────────────────────────────────┘
    ↓
    ├─→ ci-quality.yml (代码质量检查)
    ├─→ ci-tests.yml (单元测试)
    ├─→ ci-security.yml (安全扫描)
    ├─→ ci-performance.yml (性能测试)
    ├─→ build.yml (构建镜像)
    └─→ deploy.yml (部署)
    ↓
┌─────────────────────────────────────────────────────────────┐
│              📢 统一通知                                   │
│  - PR 评论（汇总所有结果）                                │
│  - 执行摘要                                               │
└─────────────────────────────────────────────────────────────┘
```

## Workflow 文件说明

### 中央调度器
| 文件名 | 类型 | 说明 |
|--------|------|------|
| `ci-scheduler.yml` | 中央调度器 | 唯一入口点，智能调度所有子工作流 |

### 子工作流（可调用）
| 文件名 | 类型 | 说明 |
|--------|------|------|
| `ci-quality.yml` | 子工作流 | 代码质量检查（ESLint、Prettier、Black、isort、Pylint、mypy） |
| `ci-tests.yml` | 子工作流 | 单元测试（前端 Vitest、后端 Pytest） |
| `ci-security.yml` | 子工作流 | 安全扫描（npm audit、Bandit、Safety、CodeQL） |
| `ci-performance.yml` | 子工作流 | 性能测试（前端构建分析、后端性能测试） |
| `build.yml` | 子工作流 | 构建镜像（前端、后端） |
| `deploy.yml` | 子工作流 | 部署（测试环境、生产环境） |

### 已禁用的旧工作流（备份）
| 文件名 | 状态 | 说明 |
|--------|------|------|
| `build-and-deploy.yml.disabled` | 已禁用 | 旧的完整流水线，已替换为中央调度器模式 |
| `test.yml.disabled` | 已禁用 | 旧的快速测试工作流 |
| `security.yml.disabled` | 已禁用 | 旧的安全检查工作流 |

## 触发条件

### 中央调度器（ci-scheduler.yml）

| 触发条件 | 说明 |
|---------|------|
| pull_request 到 main | 执行所有检查，部署到测试环境 |
| push 到 main | 执行所有检查，部署到生产环境 |
| push 到 develop | 执行所有检查，部署到测试环境 |
| push 到其他分支 | 仅执行基础检查（质量、测试） |
| 手动触发（workflow_dispatch） | 用户自定义选择执行的检查项 |

## 调度策略

根据触发条件自动选择执行的检查项：

| 触发条件 | 代码质量 | 单元测试 | 安全扫描 | 性能测试 | 构建 | 部署 |
|---------|---------|---------|---------|---------|------|------|
| push 到 feature 分支 | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| pull_request 到 main | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| push 到 develop | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (staging) |
| push 到 main | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (production) |
| 手动触发 | 🔘 用户选择 | 🔘 用户选择 | 🔘 用户选择 | 🔘 用户选择 | 🔘 用户选择 | 🔘 用户选择 |

## 手动触发

在 GitHub Actions 页面，选择 "CI 中央调度器" workflow，点击 "Run workflow"：

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| run_quality | boolean | true | 运行代码质量检查 |
| run_tests | boolean | true | 运行单元测试 |
| run_security | boolean | true | 运行安全扫描 |
| run_performance | boolean | false | 运行性能测试 |
| run_build | boolean | false | 运行构建 |
| run_deploy | boolean | false | 运行部署 |
| deploy_environment | choice | staging | 部署环境（staging/production） |
| version | string | - | 版本号（如 v1.0.0） |

## 工作流程示例

### 场景 1：创建 PR 到 main

```
开发者创建 PR：feature/xxx → main
    ↓
触发 ci-scheduler.yml
    ↓
决策执行：quality ✅, tests ✅, security ✅, performance ✅, build ✅, deploy ❌
    ↓
并行执行子工作流：
  ├─ ci-quality.yml (代码质量检查)
  ├─ ci-tests.yml (单元测试)
  ├─ ci-security.yml (安全扫描)
  └─ ci-performance.yml (性能测试)
    ↓
执行 build.yml (构建镜像)
    ↓
在 PR 中评论执行结果（统一通知）
    ↓
完成
```

### 场景 2：推送代码到 develop

```
开发者推送代码到 develop 分支
    ↓
触发 ci-scheduler.yml
    ↓
决策执行：quality ✅, tests ✅, security ✅, performance ✅, build ✅, deploy ✅ (staging)
    ↓
执行完整流程（同场景 1，但包含部署）
    ↓
部署到测试环境
    ↓
完成
```

### 场景 3：推送代码到 main

```
开发者推送代码到 main 分支
    ↓
触发 ci-scheduler.yml
    ↓
决策执行：quality ✅, tests ✅, security ✅, performance ✅, build ✅, deploy ✅ (production)
    ↓
执行完整流程
    ↓
部署到生产环境
    ↓
完成
```

### 场景 4：推送代码到 feature 分支

```
开发者推送代码到 feature/xxx 分支
    ↓
触发 ci-scheduler.yml
    ↓
决策执行：quality ✅, tests ✅, security ❌, performance ❌, build ❌, deploy ❌
    ↓
仅执行基础检查：
  ├─ ci-quality.yml (代码质量检查)
  └─ ci-tests.yml (单元测试)
    ↓
完成
```

### 场景 5：手动触发

```
开发者手动触发 workflow_dispatch
    ↓
选择要执行的检查项：
  - run_quality: true
  - run_tests: true
  - run_security: true
  - run_performance: false
  - run_build: false
  - run_deploy: false
    ↓
根据用户选择执行相应的工作流
    ↓
完成
```

## 通知机制

### PR 评论（统一通知）

- **触发时机**: PR 创建或更新时
- **通知内容**:
  - 整体执行状态（成功/失败）
  - 各检查项的执行结果
  - 链接到各个子工作流的详细日志
  - 部署信息（如果执行了部署）

### GitHub Actions 执行摘要

- **触发时机**: 每次工作流执行完成
- **内容**:
  - 执行信息（触发事件、分支、提交、执行时间）
  - 各检查项的执行结果（表格形式）

### 对比：改造前 vs 改造后

| 项目 | 改造前 | 改造后 |
|------|--------|--------|
| 通知数量 | 6+ 封邮件 | 1 封汇总通知 |
| 工作流数量 | 6 个并行工作流 | 1 个调度器 + 按需调用子工作流 |
| 资源使用 | 重复 checkout、重复安装依赖 | 共享上下文、避免重复执行 |
| 可追踪性 | 分散的结果，难以汇总 | 统一的执行摘要，一目了然 |

## 代码质量检查

### 前端检查

- **ESLint**: 代码规范检查
- **Prettier**: 代码格式检查
- **检查范围**: `my_blog_frontend/src/`

### 后端检查

- **Black**: 代码格式检查
- **isort**: 导入排序检查
- **Pylint**: 代码质量检查
- **mypy**: 类型检查
- **检查范围**: `my_blog_backend/`

## 测试

### 前端测试

- **测试框架**: Vitest
- **测试覆盖率**: 生成覆盖率报告
- **报告保留**: 30 天

### 后端测试

- **测试框架**: Pytest
- **测试类型**: 单元测试、集成测试
- **测试覆盖率**: 生成 HTML 和 XML 覆盖率报告
- **报告保留**: 30 天

### 集成测试

- **测试范围**: API 集成测试、服务间通信测试
- **测试目录**: `my_blog_backend/tests/integration/`

## 安全扫描

### 依赖漏洞扫描

- **前端**: npm audit（审计级别：moderate）
- **后端**: Safety check

### 代码安全分析

- **Bandit**: Python 代码安全分析
- **CodeQL**: JavaScript + Python 静态分析

### 镜像安全扫描

- **Trivy**: Docker 镜像漏洞扫描
- **扫描结果**: 上传为 SARIF 格式

### 报告保留

- 所有安全报告保留 30 天

## 性能测试

### 前端性能

- **构建时间**: 记录构建时间
- **Bundle 体积**: 分析构建产物大小
- **构建产物**: 上传为 artifact（保留 7 天）

### 后端性能

- **测试工具**: Locust（占位符）
- **测试类型**: 负载测试、压力测试
- **测试脚本**: 需要配置实际的性能测试脚本

## 镜像构建

### 镜像仓库

- **仓库地址**: `crpi-furbxf8d6ydk7jxx.cn-shanghai.personal.cr.aliyuncs.com/jamsyan/blog`
- **认证方式**: GitHub Secrets（`ALIYUN_USERNAME`, `ALIYUN_PASSWORD`）

### 镜像命名

- **后端**: `crpi-furbxf8d6ydk7jxx.cn-shanghai.personal.cr.aliyuncs.com/jamsyan/blog/backend`
- **前端**: `crpi-furbxf8d6ydk7jxx.cn-shanghai.personal.cr.aliyuncs.com/jamsyan/blog/frontend`

### 镜像标签

- **PR**: `pr-<number>-<sha>`（如 `pr-123-abc1234`）
- **分支**: `<branch>-<sha>`（如 `main-abc1234`）
- **语义化版本**: `v<version>`（如 `v1.0.0`）
- **latest**: 仅 main 分支

### 多架构支持

- **支持平台**: linux/amd64, linux/arm64
- **构建方式**: Docker Buildx

### 缓存优化

- **层缓存**: GitHub Actions cache
- **缓存模式**: max（最大化缓存）

## 部署流程

### 测试环境部署

1. **拉取镜像**: 从阿里云镜像仓库拉取最新镜像
2. **创建配置**: 生成 `docker-compose.override.yml`
3. **启动容器**: 使用 Docker Compose 启动服务
4. **等待启动**: 等待 30 秒让服务完全启动
5. **健康检查**: 执行 HTTP 健康检查（最多重试 30 次）
6. **验证部署**: 检查容器状态和日志
7. **清理**: 部署完成后自动清理容器

### 生产环境部署（占位符）

生产环境部署脚本为占位符，需要根据实际环境配置：

1. **服务器连接**: SSH 连接到生产服务器
2. **拉取镜像**: 从阿里云镜像仓库拉取镜像
3. **更新服务**: 使用 Docker Compose 或 Kubernetes 更新服务
4. **健康检查**: 执行健康检查
5. **回滚机制**: 失败时自动回滚

### 健康检查

- **前端**: `http://localhost:80/health`
- **后端**: `http://localhost:8000/health`
- **重试次数**: 30 次
- **重试间隔**: 5 秒

## Artifacts 管理

| Artifact 类型 | 保留时间 | 说明 |
|-------------|---------|------|
| 测试覆盖率报告 | 30 天 | 前端和后端测试覆盖率 |
| 安全报告 | 30 天 | npm audit、Bandit、Safety、CodeQL 报告 |
| 构建产物 | 7 天 | 前端和后端构建产物 |

## 故障排查

### Workflow 未触发

- 检查 `.github/workflows/` 目录下的文件名是否正确（不能有 `.disabled` 后缀）
- 检查触发条件是否满足
- 查看 GitHub Actions 日志

### 代码检查失败

- 查看具体检查步骤的日志
- 本地运行相同的检查命令：
  - 前端：`npm run lint`, `npm run format:check`
  - 后端：`black --check .`, `pylint .`
- 修复问题后重新提交

### 测试失败

- 查看测试日志定位失败用例
- 本地运行测试：`npm run test` 或 `pytest`
- 修复问题后重新提交

### 镜像构建失败

- 检查 Dockerfile 是否正确
- 检查镜像仓库凭证是否配置（`ALIYUN_USERNAME`, `ALIYUN_PASSWORD`）
- 查看构建日志定位问题
- 检查网络连接

### 部署失败

- 检查健康检查端点是否正确
- 查看容器日志：`docker-compose logs`
- 检查端口是否正确（前端 80，后端 8000）
- 查看部署日志定位问题

### 安全扫描失败

- 查看安全报告了解漏洞详情
- 更新有漏洞的依赖
- 修复代码安全问题
- 重新提交

## 最佳实践

### 1. 分支策略

- `main` - 生产分支，只接受 PR 合并
- `develop` - 开发分支，日常开发
- `feature/*` - 功能分支，从 develop 创建

### 2. 提交规范

- 提交信息清晰描述变更内容
- PR 标题简洁明了
- 代码审查通过后再合并

### 3. 版本发布

- 使用语义化版本号（v1.0.0）
- 发布前确保所有检查通过
- 发布后监控服务状态

### 4. 安全

- 定期更新依赖
- 关注安全扫描报告
- 及时修复漏洞
- 使用强密码

### 5. 性能

- 关注构建时间
- 监控镜像大小
- 优化依赖
- 使用缓存

## 配置要求

### 必需的 GitHub Secrets

- `ALIYUN_USERNAME`: 阿里云镜像仓库用户名
- `ALIYUN_PASSWORD`: 阿里云镜像仓库密码

### 可选的 GitHub Secrets

- `SLACK_WEBHOOK`: Slack 通知 Webhook
- `DINGTALK_WEBHOOK`: 钉钉通知 Webhook
- `SSH_PRIVATE_KEY`: 生产服务器 SSH 私钥（生产环境部署需要）
- `SSH_HOST`: 生产服务器地址（生产环境部署需要）
- `SSH_USER`: 生产服务器用户名（生产环境部署需要）

详细配置说明请参考 [GitHub Secrets 配置指南](./github-secrets-setup.md)。

## 参考资料

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Docker 官方文档](https://docs.docker.com/)
- [阿里云容器镜像服务文档](https://help.aliyun.com/product/60716.html)
- [GitHub Secrets 配置指南](./github-secrets-setup.md)
- [容器镜像管理](./容器镜像管理.md)
- [项目 README](../../README.md)
