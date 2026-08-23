# 断点续审与指纹复用 (Resume & Fingerprint Reuse)

- ID: `eng-resume`
- 类型: 方法机制
- 来源: 审查引擎
- 分组: G-B · 审查引擎
- 阶段: 高级 advanced

> sha256(mode+old+new+diffText) 指纹复用已完成文件评论；SealedInput 冻结 commit 端点防 ref 漂移

## 核心主张 (what)

- 断点续审通过任务指纹复用跳过已完成审查，从断点继续执行未决项
- reviewItemFingerprint = sha256(mode + oldPath + newPath + diffText)，是评审项的确定性身份指纹
- 父 manifest 中标记 completed/reused 的评论直接回填 Collector（复用），未决项重跑
- scanItemFingerprint = sha256(full_scan + path + content)，是全文件扫描项的指纹
- SealedInput 冻结 commit 端点，防止 ref 移动导致身份漂移
- 用法入口：ocr review --resume <session-id>

## 为什么 (why)

- 大仓库/长会话中断后从头重审成本极高，指纹复用把已完成工作降为 O(1) 回填
- 指纹基于内容与路径而非时间，同一 diff 多次审查指纹一致，天然幂等
- SealedInput 冻结端点解决审查进行中远端 ref 更新导致的前后身份不一致
- 复用/重跑决策由父 manifest 状态驱动，覆盖度契约是单一事实源

## 如何实践 (how)

- 生成评审项指纹 reviewItemFingerprint=sha256(mode+oldPath+newPath+diffText)，作为任务身份标识
- 续审时查询父 manifest：条目状态为 completed 或 reused 的评论直接回填 Collector，不重新调用 LLM
- 未决（pending/failed）条目重新执行审查子任务
- scan 模式生成 scanItemFingerprint=sha256(full_scan+path+content) 标识扫描项用于复用
- SealedInput 在会话启动时冻结 commit 端点（commit hash 级别），后续引用不变
- 执行入口 ocr review --resume <session-id> 指定要恢复的会话

## 案例 (cases)

- 30 文件审查跑到第 25 个断网，--resume 后 25 个 completed 指纹直接回填，仅重跑 5 个
- 同一 diff 被评审两次（如重复提交），指纹一致直接复用评论，无重复 LLM 开销
- 审查中远端仓库被 push 新 commit，SealedInput 保证本会话仍引用冻结端点，评论身份不漂移
- scan 模式下文件内容未变的扫描项按 scanItemFingerprint 复用，仅重扫变化文件

## 反模式/易错点

- 指纹遗漏 diffText 或 mode 分量，同一 diff 不同模式产出相同指纹，错误复用评论
- 不检查父 manifest 状态直接复用，failed 条目被当 completed 回填污染评论集
- 依赖可变 ref（如分支名）而非冻结 commit 端点，审查期间 ref 移动导致身份漂移、评论错位
- 续审时重建全部会话而非按指纹差量续跑，退化为全量重审

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| eng-session → eng-resume | 前置依赖 | 续审依赖会话持久化 |
| eng-manifest → eng-resume | 前置依赖 | 复用必须过父 manifest |
| eng-resume → cli-review | 前置依赖 | review 支持 --resume 续审 |
