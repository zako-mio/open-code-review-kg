# ocr 命令总览与安装 (CLI Overview & Install)

- ID: `cli-overview`
- 类型: 工具
- 来源: 命令行
- 分组: G-C · 命令行工具
- 阶段: 基础 basic

> 安装方式（npm/脚本/二进制/源码）、cobra 命令树、全局参数与 version/completion 子命令

## 核心主张 (what)

- ocr 是阿里巴巴开源的 AI 代码审查 CLI 工具（项目 alibaba/open-code-review），以 Go 编写，命令名为 ocr，面向开发者提供本地化、可自定义的代码审查能力
- 基于 cobra 构建的命令树，顶层子命令包括 review（核心审查）、scan（全文件扫描）、delegate（委托模式）、config（配置管理）、session（会话管理）、llm（LLM 工具）、rules（规则调试）、viewer（WebUI 查看器）、completion（shell 补全）、version（版本信息）
- 官方推荐安装方式为 npm 全局安装：npm install -g @alibaba-group/open-code-review，该方式对 Node 环境用户最便捷
- 硬性前置条件为 Git 版本不低于 2.41，工具底层大量依赖 git diff、git 搜索与仓库操作能力，版本不足将直接导致功能不可用
- 提供多条安装路径以适应不同环境：install.sh / install.ps1 脚本安装、GitHub Release 预编译二进制、源码构建（Makefile）
- 根命令支持 -V / --version 查看版本号，--help 查看完整命令树与参数说明，是熟悉工具的第一步

## 为什么 (why)

- 统一入口封装了多种审查模式（review/scan/delegate）与配套管理能力（config/session/llm/rules/viewer），避免用户为每种能力安装独立工具
- Git>=2.41 的版本门槛保证了 diff 解析、变更搜索、仓库操作等底层原语的稳定性，是审查准确性的基础保障
- 多安装方式（npm/脚本/二进制/源码）覆盖 Linux、macOS、Windows 及无包管理器的受限环境，降低接入成本

## 如何实践 (how)

- npm install -g @alibaba-group/open-code-review 全局安装，随后直接执行 ocr 命令
- 先执行 git --version 核对 Git 版本是否满足 >=2.41，不满足则先升级 Git 再安装
- 无 npm 环境时执行 curl 下载 install.sh（Linux/macOS）或 install.ps1（Windows）脚本安装
- 从 GitHub Releases 页面下载对应操作系统与架构的预编译二进制，解压后放入 PATH
- 源码方式：git clone 仓库后按 Makefile 目标执行构建（如 make build），生成二进制
- 安装后执行 ocr -V 或 ocr --version 验证安装成功，执行 ocr --help 浏览命令树
- 执行 ocr completion <shell> 生成对应 shell 的补全脚本，提升日常使用效率

## 案例 (cases)

- 开发机快速上手：单条 npm install -g 命令完成安装，随后 ocr --version 验证即开始使用
- CI 服务器或 Docker 镜像构建场景：Git 版本常较旧，先升级 Git 到 2.41+，再用 GitHub Release 二进制或脚本安装，避免 npm 依赖
- Windows 开发环境：使用 install.ps1 脚本或下载 exe 二进制，绕过 npm/Git 工具链兼容问题
- 内网/离线环境：预先下载 Release 二进制离线分发，源码构建则需预置 Go 工具链

## 反模式/易错点

- 忽略 Git 版本前置条件：在 Git<2.41 的环境直接安装，运行 review/scan 时报错后才发现是底层 git 能力不足，应先 git --version 检查
- 二进制安装后未加入 PATH 或 PATH 顺序错误，执行 ocr 提示 command not found，误以为安装失败而重复安装
- 多安装方式混用导致版本混乱：npm 全局版与 Release 二进制同时存在，PATH 优先命中旧版本，行为与文档不符，应统一保留一种安装方式并核对版本

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| cli-overview → cli-review | 前置依赖 | 安装后先学 review |
| cli-overview → cli-scan | 前置依赖 | 安装后学 scan |
| cli-overview → cli-config | 前置依赖 | 用前必须配置模型 |
