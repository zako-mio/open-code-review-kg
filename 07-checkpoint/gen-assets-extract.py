#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 open-code-review 源码提取精选实践资产到 assets/（复制小文件 + 节选大文件）"""
import os, re, json, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)          # 图谱根目录
SRC = os.path.join(ROOT, 'open-code-review')
ASSETS = os.path.join(ROOT, 'assets')

# (type, src_rel, dst_rel, desc, [node_ids], excerpt)
# excerpt=True 表示大文件节选（生成 .md 摘要 + 关键符号表）
ASSET_LIST = [
    # ---- CI 集成 ----
    ('ci', 'examples/github_actions/ocr-review.yml', 'ci/github_actions-ocr-review.yml',
     'GitHub Actions 自动审查 workflow 示例（PR 事件+评论触发，并发组防重）', ['int-gha', 'use-pr-review', 'use-ci'], False),
    ('ci', 'examples/gitlab_ci/.gitlab-ci.yml', 'ci/gitlab-ci.yml',
     'GitLab CI 审查作业示例（含 OCR_* 环境变量族）', ['int-cicd', 'use-ci'], False),
    ('ci', 'examples/gerrit_ci/Jenkinsfile', 'ci/gerrit-Jenkinsfile',
     'Gerrit 评审流 Jenkinsfile 示例', ['int-cicd'], False),
    ('ci', 'examples/codeup_ci/codeup-flow.yml', 'ci/codeup-flow.yml',
     '阿里云 Codeup CI 示例', ['int-cicd'], False),
    ('ci', 'examples/gitflic_ci/gitflic-ci.yaml', 'ci/gitflic-ci.yaml',
     'GitFlic CI 示例', ['int-cicd'], False),
    ('ci', 'examples/bitbucket_pipelines/bitbucket-pipelines.yml', 'ci/bitbucket-pipelines.yml',
     'Bitbucket Pipelines 示例', ['int-cicd'], False),
    ('ci', 'action.yml', 'ci/action.yml',
     'GitHub Actions composite action 完整定义（24 入参 / 6 出参）', ['int-gha', 'use-ci'], False),
    ('script', 'scripts/github-actions/post-review-comments.js', 'scripts/post-review-comments.js',
     'GHA 评论发布脚本（sticky 摘要 / 增量 IoU 去重 / 50 条批量 / severity 路由）', ['int-gha'], False),
    # ---- 工具 schema ----
    ('tool', 'internal/config/toolsconfig/tools.json', 'tools/tools.json',
     '6 个审查专用工具 schema 权威源（plan_task/main_task 相位旗标）', ['arch-grounded-tools', 'cli-review'], False),
    # ---- 提示词 ----
    ('prompt', 'internal/config/template/prompts/review_filter_task_user.md', 'prompts/review_filter_task_user.md',
     '独立反思过滤 prompt 原文（五步法 / Ground A/B / 非对称信息边界）', ['arch-reflection'], False),
    # ---- 规则 ----
    ('rule', 'internal/config/rules/system_rules.json', 'rules/system_rules.json',
     '内置系统规则（四层规则链最底层，首匹配优先）', ['cfg-rules-chain', 'arch-dispatch'], False),
    # ---- 核心代码节选 ----
    ('code', 'internal/agent/agent.go', 'code/agent.go.md',
     'agent.go 核心节选：Run 流水线 / dispatchSubtasks / executeSubtask / REVIEW_FILTER', ['arch-pipeline', 'arch-dispatch', 'arch-parallel', 'arch-reflection'], True),
    ('code', 'internal/llmloop/loop.go', 'code/llmloop-loop.go.md',
     'ReAct 主循环节选：RunPerFile / 终止条件 / 工具分派 / 异步评论', ['arch-grounded-tools', 'eng-compression'], True),
    ('code', 'internal/llmloop/compression.go', 'code/llmloop-compression.go.md',
     '三区内存压缩节选：frozen/compress/active + 60%/80% 双阈值', ['eng-compression'], True),
    ('code', 'internal/diff/resolver.go', 'code/diff-resolver.go.md',
     '行号解析五级回退链节选：ResolveComment / matchConsecutive', ['eng-locator'], True),
    ('code', 'internal/diff/relocation.go', 'code/diff-relocation.go.md',
     '跨文件与 LLM 重定位节选：RelocateAcrossFiles / ReLocateComment', ['eng-relocate'], True),
    ('code', 'internal/diff/git.go', 'code/diff-git.go.md',
     '三种 diff Provider 节选：range / commit / workspace', ['eng-diff'], True),
    ('code', 'internal/scan/agent.go', 'code/scan-agent.go.md',
     '全文件扫描引擎节选：Run 时序 / DEDUP / PROJECT_SUMMARY', ['eng-scan', 'cli-scan'], True),
    ('code', 'internal/session/manifest.go', 'code/session-manifest.go.md',
     'Run Manifest 覆盖度契约节选：RegisterSelected / FailureClass', ['eng-manifest', 'eng-session'], True),
    ('code', 'internal/session/resume.go', 'code/session-resume.go.md',
     '断点续审节选：指纹复用 / SealedInput 冻结', ['eng-resume'], True),
    ('code', 'internal/llm/resolver.go', 'code/llm-resolver.go.md',
     '5 级配置优先级解析节选：ResolveEndpointWithOptions', ['cfg-priority'], True),
    ('code', 'internal/llm/providers.go', 'code/llm-providers.go.md',
     '27 个内置 provider 注册表节选', ['cfg-providers'], True),
    ('code', 'internal/llm/protocol.go', 'code/llm-protocol.go.md',
     '4 种 LLM 协议定义节选', ['cfg-protocol'], True),
    ('code', 'internal/mcp/client.go', 'code/mcp-client.go.md',
     'MCP 双传输客户端节选：stdio / Streamable HTTP', ['cfg-mcp'], True),
    ('code', 'internal/viewer/server.go', 'code/viewer-server.go.md',
     'viewer 服务器节选：路由 / hostGuard 防 DNS-rebind', ['cli-viewer', 'q-security'], True),
    ('code', 'internal/telemetry/provider.go', 'code/telemetry-provider.go.md',
     'OpenTelemetry 双管道初始化节选', ['q-telemetry'], True),
    ('code', 'internal/gitcmd/runner.go', 'code/gitcmd-runner.go.md',
     'git 子进程并发限流（默认 16）', ['eng-diff'], True),
    # ---- 插件与 Skill ----
    ('skill', 'skills/open-code-review/SKILL.md', 'skills/SKILL-review.md',
     '通用 review skill：四步 review/filter/fix/report + severity×category 分级', ['int-skill', 'use-no-key'], False),
    ('skill', 'skills/open-code-review-delegate/SKILL.md', 'skills/SKILL-delegate.md',
     '委托审查 skill：preview→rule→git diff→逐文件→格式化→覆盖率', ['int-skill', 'cli-delegate'], False),
    ('plugin', 'plugins/open-code-review/opencode/open-code-review.ts', 'plugins/opencode-plugin.ts',
     'OpenCode 原生插件源码（@opencode-ai/plugin，参数互斥校验）', ['int-opencode'], False),
    ('plugin', '.claude/commands/open-code-review.md', 'plugins/claude-slash-command.md',
     'Claude Code 斜杠命令定义', ['int-claude'], False),
    ('plugin', '.codex-plugin/plugin.json', 'plugins/codex-plugin.json',
     'Codex 插件清单（skills + Read capability + defaultPrompt）', ['int-codex'], False),
    ('plugin', '.cursor-plugin/plugin.json', 'plugins/cursor-plugin.json',
     'Cursor 插件清单（复用 ../skills/）', ['int-cursor'], False),
    ('plugin', 'qca/system-prompt.md', 'plugins/qca-system-prompt.md',
     'QCA Forward 委托系统提示（只允许 delegate preview/rule）', ['int-qca'], False),
    # ---- 构建发布 ----
    ('build', 'Makefile', 'build/Makefile',
     '构建链：build / test(race) / coverage(90% 门禁) / build-all 6 平台交叉编译', ['q-release'], False),
    ('build', 'install.sh', 'build/install.sh',
     'Linux/macOS 安装脚本（latest tag + sha256 校验 + OCR_GITHUB_MIRROR）', ['cli-overview', 'q-release'], False),
    ('build', 'install.ps1', 'build/install.ps1',
     'Windows 安装脚本（PowerShell 5.1+）', ['cli-overview', 'q-release'], False),
    ('build', 'package.json', 'build/package.json',
     'npm 包定义（bin: ocr → bin/ocr.js）', ['q-release', 'cli-overview'], False),
    ('build', 'go.mod', 'build/go.mod',
     'Go 依赖清单（cobra / anthropic-sdk-go / openai-go / MCP go-sdk / otel 等）', ['q-release'], False),
    # ---- 文档 ----
    ('doc', 'README.zh-CN.md', 'doc/README.zh-CN.md',
     '官方中文 README（定位/基准/设计理念/快速开始）', ['cli-overview'], False),
]

SYMBOL_RE = re.compile(r'^(func|type|const|var)\s+\w+')


def excerpt(src_path, dst_rel):
    """大文件节选：头部注释 + 关键符号定义（func/type/const/var），带行号标注"""
    lines = open(src_path, encoding='utf-8').read().split('\n')
    total = len(lines)
    head = lines[:30]
    symbols = []
    for i, ln in enumerate(lines, 1):
        if SYMBOL_RE.match(ln.strip()):
            symbols.append('%6d  %s' % (i, ln.rstrip()))
    out = []
    out.append('# 源码节选（自动生成，非完整文件）')
    out.append('')
    out.append('- 源文件: `%s`' % os.path.relpath(src_path, ROOT))
    out.append('- 总行数: %d | 节选: 头部 %d 行 + %d 个关键符号' % (total, len(head), len(symbols)))
    out.append('- 完整源码见 `open-code-review/`（同留档目录）')
    out.append('')
    out.append('## 文件头')
    out.append('')
    out.append('```go')
    out.extend(head)
    out.append('```')
    out.append('')
    out.append('## 关键符号（行号 → 定义）')
    out.append('')
    out.append('```go')
    out.extend(symbols[:120])
    out.append('```')
    out.append('')
    return '\n'.join(out)


def main():
    os.makedirs(ASSETS, exist_ok=True)
    manifest = []
    for typ, src_rel, dst_rel, desc, node_ids, is_excerpt in ASSET_LIST:
        src_path = os.path.join(SRC, src_rel)
        dst_path = os.path.join(ASSETS, dst_rel)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        if not os.path.exists(src_path):
            print('!! 源缺失:', src_rel)
            continue
        if is_excerpt:
            content = excerpt(src_path, dst_rel)
            with open(dst_path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            shutil.copy2(src_path, dst_path)
        size = os.path.getsize(dst_path)
        manifest.append({
            'id': 'asset-%02d' % len(manifest),
            'type': typ,
            'name': os.path.basename(dst_rel),
            'path': 'assets/' + dst_rel,
            'src_path': src_rel,
            'desc': desc,
            'node_ids': node_ids,
            'size_bytes': size,
        })
        print('asset: %-14s %-55s %7d B' % (typ, dst_rel, size))
    with open(os.path.join(ROOT, 'assets-manifest.json'), 'w', encoding='utf-8') as f:
        json.dump({'meta': {'generated': '2026-08-23', 'total_assets': len(manifest)},
                   'assets': manifest}, f, ensure_ascii=False, indent=1)
    print('assets-manifest.json:', len(manifest), 'assets')


if __name__ == '__main__':
    main()