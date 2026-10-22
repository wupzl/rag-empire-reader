# 技术校正与阅读约定

整理日期：2026-10-23。原稿完整保存在 source/original.md。阅读版统一章节层级、删除生成提示和重复预告，九章完结，不包含 Agent 续篇预告。

## 安全边界

RLS 不能笼统视为任何身份都无法绕过的防线：超级用户与 BYPASSRLS 角色绕过行安全，表所有者通常也绕过；FORCE ROW LEVEL SECURITY 可使表所有者受策略约束。应用连接应使用最小权限角色，并验证连接池的事务与租户上下文边界。[PostgreSQL 官方文档](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)。

检索文档属于不可信输入。提示词隔离、过滤、输出验证和最小权限需要组合使用，不能声称完全消除提示注入风险。[OWASP RAG 安全指南](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html)。

## 评测口径

Faithfulness 衡量回答是否得到上下文支持，不等同于现实正确性。Context Recall 可按参考答案中的主张是否被检索上下文支持计算，与文档集合 Recall@K 的口径不同。Ragas 的接口随版本变化，正文代码作为教学示意，运行时需固定依赖并按照相应版本调整。[Ragas 官方指标文档](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/)。

## 实验与代码

所有工具使用确定性的浏览器本地计算。成本单价由读者输入，不代表任何供应商当前报价。容量估算忽略突发、长尾、重试与资源竞争，不能替代压测。A/B 实验使用独立样本、固定样本量的双比例正态近似；小样本、重复窥视、相关样本需要其他方法。代码片段不是完整可部署的后端项目。故事中的年份、事故和性能数字属于叙事设定。
