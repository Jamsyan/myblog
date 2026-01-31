# 贡献指南

## 欢迎贡献

感谢您对 LinkGateway 项目的关注！我们欢迎任何形式的贡献，包括但不限于：

- 🐛 Bug 修复
- ✨ 新功能开发
- 📝 文档改进
- 🎨 代码重构和优化
- 🧪 测试用例补充

## 开发流程

### 1. Fork 项目
```bash
git clone https://github.com/yourusername/myblog.git
cd myblog
git checkout -b feature/your-feature-name
```

### 2. 遵循代码规范
在开始开发前，请务必阅读并遵循以下规范文档：

- [后端开发规范](./03-开发规范/01-后端开发规范.md)
- [代码审查规范](./03-开发规范/02-代码审查规范.md)
- [代码质量标准](./03-开发规范/04-代码质量标准.md)

### 3. 编写代码

#### 3.1 代码质量要求
- ✅ 嵌套层级不超过 3 层
- ✅ 方法长度不超过 50 行
- ✅ 使用守护判断而非深层嵌套
- ✅ 遵循单一职责原则
- ✅ 添加必要的文档字符串
- ✅ 异常处理清晰，避免吞掉异常

#### 3.2 代码风格要求
- ✅ 命名规范（PascalCase、camelCase、UPPER_SNAKE_CASE）
- ✅ 代码组织清晰
- ✅ 适当的注释和文档

### 4. 运行测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_xxx.py
```

### 5. 提交代码
```bash
git add .
git commit -m "feat: 添加新功能"

# 提交类型
- feat: 新功能
- fix: Bug 修复
- docs: 文档更新
- style: 代码格式调整（不影响代码运行）
- refactor: 重构
- test: 测试相关
- chore: 构建过程或辅助工具变动
```

### 6. 推送代码
```bash
git push origin feature/your-feature-name
```

## 代码审查要点

每次提交代码时，请确保：

- [ ] 嵌套层级是否超过 3 层
- [ ] 方法长度是否超过 50 行
- [ ] 是否使用了守护判断而非深层嵌套
- [ ] 异常处理是否清晰
- [ ] 是否有必要的文档字符串
- [ ] 是否遵循单一职责原则
- [ ] 是否有重复代码
- [ ] 变量命名是否有意义
- [ ] 是否使用了类型注解
- [ ] 是否有单元测试覆盖

## Pull Request 要求

提交 PR 时，请确保：

1. **标题清晰**：使用 `[类型] 简短描述` 格式
2. **描述详细**：说明修改的内容、原因和影响
3. **关联 Issue**：如果修复 Bug，关联对应的 Issue
4. **代码审查**：至少一人审查通过
5. **测试通过**：所有测试必须通过
6. **文档更新**：如有需要，更新相关文档

## 代码审查清单

基于[代码审查规范](./03-开发规范/02-代码审查规范.md)，每次代码审查时必须检查：

### 代码质量标准
- [ ] 嵌套层级是否超过 3 层
- [ ] 方法长度是否超过 50 行
- [ ] 认知复杂度是否超过 10
- [ ] 是否使用了守护判断而非深层嵌套
- [ ] 异常处理是否清晰
- [ ] 是否有必要的文档字符串
- [ ] 是否遵循单一职责原则
- [ ] 是否有重复代码

### 代码异味检查
- [ ] 是否有过长方法（超过 50 行）
- [ ] 是否有深层嵌套（超过 3 层）
- [ ] 是否有重复代码
- [ ] 是否有魔法数字
- [ ] 是否有过长参数列表
- [ ] 是否有临时变量
- [ ] 是否有注释掉的代码
- [ ] 是否有全局变量滥用
- [ ] 是否有过度耦合

### 代码可读性
- [ ] 变量命名是否有意义
- [ ] 代码结构是否清晰
- [ ] 是否有必要的注释
- [ ] 代码是否像读文章一样流畅

## 项目结构

```
myblog/
├── my_blog_backend/
│   └── LinkGateway/
│       ├── __init__.py
│       ├── api_mapper.py
│       ├── auth.py
│       ├── db_link.py
│       ├── gateway.py
│       ├── inner_comm.py
│       ├── logs.py
│       ├── outer_comm.py
│       ├── path_manager.py
│       ├── plugin.py
│       ├── protocol.py
│       ├── registry.py
│       ├── service_comm.py
│       ├── service_proxy.py
│       └── standards.py
├── Docs/
│   ├── 01-项目概述/
│   ├── 02-架构设计/
│   ├── 03-开发规范/
│   │   ├── 01-后端开发规范.md
│   │   ├── 02-代码审查规范.md
│   │   ├── 04-代码质量标准.md
│   ├── 04-后端开发/
│   ├── 05-前端开发/
│   ├── 06-API文档/
│   ├── 07-设计规范/
│   ├── 08-最佳实践/
│   └── README.md
└── README.md
```

## 联系方式

- 📧 提 Issue：报告 Bug 或提出新功能
- 💬 讨论：在 Issue 中讨论技术方案
- 📧 Pull Request：提交代码改进
- 📧 邮件：发送重要问题到项目维护者

## 开发工具

### 推荐的开发环境
- **IDE**：PyCharm、VS Code
- **Python 版本**：3.8+
- **代码格式化**：Black
- **代码检查**：Pylint、Flake8
- **类型检查**：MyPy

### 代码质量工具

```bash
# 安装代码检查工具
pip install pylint flake8 mypy black radon vulture

# 运行代码检查
pylint my_blog_backend/LinkGateway/
flake8 my_blog_backend/LinkGateway/
mypy my_blog_backend/LinkGateway/
black --check my_blog_backend/LinkGateway/
radon cc my_blog_backend/LinkGateway/
vulture my_blog_backend/LinkGateway/
```

## 行为准则

### 尊重他人
- 尊重其他贡献者的代码和意见
- 建设性地提出问题和建议
- 避免人身攻击或负面言论

### 专业态度
- 保持专业和友好的沟通
- 及时回应问题和反馈
- 愿意学习和改进

### 协作精神
- 主动帮助他人
- 分享知识和经验
- 共同提升项目质量

## 参考资源

- [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Clean Code by Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Principles-Patterns-Practices/dp/0132019171)

## 许可证

本项目采用 MIT 许可证，贡献的代码将遵循相同的许可。

---

感谢您的贡献！让我们一起把 LinkGateway 打造成更好的项目！