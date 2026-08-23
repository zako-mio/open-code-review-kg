# ocr rules (ocr rules)

- ID: `cli-rules`
- 类型: 工具
- 来源: 命令行
- 分组: G-C · 命令行工具
- 阶段: 高级 advanced

> 规则调试：rules check <file> 显示命中规则层（custom/project/global/system）与匹配模式

## 核心主张 (what)

- ocr rules 是规则调试命令，核心子命令为 check：ocr rules check <file-path> 显示指定文件命中的规则层与匹配模式
- 输出明确区分规则层级：custom（自定义规则）、project（项目级规则）、global（全局规则）、system（系统内置规则）四层，说明每层命中的具体规则与匹配模式
- 用于回答'为什么这个文件被这样审查'：把某个文件的审查结果与规则命中对齐，定位结论来源
- 与四层规则链配合：custom/project/global/system 从高到低构成规则体系，check 是验证该体系对具体文件生效情况的调试工具

## 为什么 (why)

- 规则分层（custom/project/global/system）与匹配模式组合复杂，肉眼难以推断某个文件最终命中哪些规则，check 提供确定性的可视验证
- 审查结论异常（该审的没审、不该审的审了）时，需要快速定位是规则问题还是模型问题，check 是第一排查手段
- 新增或修改自定义规则后，需要立即验证规则是否按预期命中目标文件，check 比跑完整审查更快更省

## 如何实践 (how)

- 检查单个文件的规则命中：ocr rules check src/foo.go
- 检查目录下文件的命中：ocr rules check internal/agent
- 解读输出：查看命中的规则层（custom/project/global/system）与每层匹配的规则 id 及匹配模式
- 修改自定义规则后重跑 check 验证生效：ocr rules check <file-path> 对比修改前后的命中变化
- 结合 delegate/rule 输出交叉验证规则结构，确认规则体系在代理与本地两条路径上一致

## 案例 (cases)

- 新加自定义规则验证：写完一条只针对 *_test.go 的规则后，ocr rules check 测试文件与非测试文件各跑一次，确认命中范围正确
- 文件被意外审查/忽略排查：某文件没被审，ocr rules check 该文件，发现被某层规则的排除模式命中，定位后修正规则
- 审查结论溯源：review 对某文件给出奇怪结论，先 check 确认规则命中是否符合预期，把规则层问题与模型判断问题分开
- 四层规则链整体校验：批量对关键文件跑 check，确认 custom 覆盖 project、project 覆盖 global、global 覆盖 system 的优先级按预期工作

## 反模式/易错点

- 改完规则不跑 check 直接跑完整 review 验证：成本高且结论混杂模型因素，应先 check 快速确认规则命中再进 review
- 忽视规则层优先级：custom 规则与 project 规则冲突时以为都生效，实际按层优先级裁决，check 输出会显示最终命中层，误读优先级导致规则'不生效'的假象
- 把 ocr rules check 当 lint 工具使用：check 只回答规则命中问题，不产出审查意见，用它替代 review/scan 会得出'规则系统正常'的错误安全感

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| cfg-rules-chain → cli-rules | 前置依赖 | rules 命令调试规则链 |
