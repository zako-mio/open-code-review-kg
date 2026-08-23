# 构建与发布体系 (Build & Release)

- ID: `q-release`
- 类型: 工程保障
- 来源: 工程保障
- 分组: G-F · 工程保障
- 阶段: 高级 advanced

> npm 包（6 平台 optionalDependencies）+ GitHub Release 二进制 + install.sh/ps1，Makefile 覆盖率 90% 门禁

## 核心主张 (what)

- npm 包 @alibaba-group/open-code-review 作为分发入口，bin 指向 bin/ocr.js，postinstall 钩子自动下载对应平台原生二进制
- 6 平台覆盖：@alibaba-group/ocr-{darwin-x64,darwin-arm64,linux-x64,linux-arm64,win32-x64,win32-arm64} 作为 optionalDependencies 按平台安装
- install.sh：经 GitHub API 解析 latest tag → 下载后 sha256sum 校验完整性 → 安装到 OCR_INSTALL_DIR（默认 /usr/local/bin），支持 OCR_VERSION 锁定版本与 OCR_GITHUB_MIRROR 镜像加速
- install.ps1：面向 PowerShell 5.1+，安装到 %LOCALAPPDATA%\Programs\ocr，免管理员权限
- Makefile 提供完整构建链：build / test(race 检测) / coverage(90% 阈值门禁，低于即失败) / vet / check / build-all(6 平台交叉编译，CGO_ENABLED=0 静态二进制) / sha256sum / dist
- 启动时后台运行 update.js 检查新版本，18 分钟冷却防频繁请求，OCR_NO_UPDATE 可禁用自动更新

## 为什么 (why)

- 单一 npm 入口 + postinstall 下载二进制，兼顾『一条命令安装』与『原生性能』，比纯 Go 发布链更贴近 JS 生态用户
- sha256sum 校验保证供应链安全，镜像变量解决部分网络环境 GitHub 不可达问题
- 90% 覆盖率门禁与 race 检测保证发布质量，交叉编译产出静态二进制降低运行时依赖
- 自动更新让用户及时获得修复与安全补丁，冷却与开关避免打扰

## 如何实践 (how)

- npm 安装：npm install -g @alibaba-group/open-code-review，postinstall 自动下载当前平台二进制
- 脚本安装（Linux/macOS）：curl -sSL https://raw.githubusercontent.com/alibaba/open-code-review/main/install.sh \| bash；自定义目录用 OCR_INSTALL_DIR=/opt/ocr，锁版本用 OCR_VERSION=v1.x.x，国内加速用 OCR_GITHUB_MIRROR
- Windows 安装：以 PowerShell 5.1+ 执行 install.ps1，二进制落于 %LOCALAPPDATA%\Programs\ocr
- 本地开发构建：make build 编译当前平台；make build-all 交叉编译 6 平台；make test 带 race 检测；make coverage 触发 90% 门禁
- 产出发布物：make sha256sum 生成校验和，make dist 打包分发包
- 禁用自动更新：设置 OCR_NO_UPDATE=1 后启动不再检查新版本，适合受控生产环境

## 案例 (cases)

- 团队统一安装：运维脚本指定 OCR_VERSION 固定版本 + sha256sum 校验，避免版本漂移
- 离线内网环境：使用 OCR_GITHUB_MIRROR 指向内网镜像完成安装与更新
- 开发迭代：make test 的 race 检测捕获并发 bug，make coverage 门禁在合并前拦截覆盖率下滑
- Windows 无管理员权限：install.ps1 装入用户目录，无需 UAC 即可使用

## 反模式/易错点

- 绕过 npm postinstall 或直接下载 GitHub Release 二进制却跳过 sha256sum 校验，供应链风险敞口
- 在代理/内网环境用默认 GitHub 地址安装失败后不换 OCR_GITHUB_MIRROR，而是改用不校验的下载方式
- CI 中每次全新安装最新版（不锁 OCR_VERSION），上游发布即影响构建结果，不可复现
- 误以为 npm 包即完整二进制而忽略 optionalDependencies 平台限制，在不支持平台上静默降级
