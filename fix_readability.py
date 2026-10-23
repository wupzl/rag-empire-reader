from pathlib import Path
import re,html
P=Path(__file__).parent
banks={
6:'''JWT 证明身份，不能证明当前用户有权读取每份文档。检索、缓存及生成前都需校验租户与文档权限。
可选独立数据库、独立 schema 或共享表加 tenant_id。隔离强度、成本与运维复杂度不同；共享方案需贯穿索引、缓存和异步任务。
RBAC 按角色授权，ABAC 按主体、资源与环境属性决策，ACL 记录具体资源对主体的许可。组合时应明确拒绝优先及继承规则。
先取全库 Top K 再过滤会造成授权结果不足，也可能让未授权数据进入后续处理。应在检索链路施加权限约束，并在生成前再次校验。
不一定。SQL 的逻辑条件不代表 ANN 索引物理执行时先过滤。应通过 EXPLAIN、选择性与召回测试评估索引、分区和迭代扫描策略。
超级用户与 BYPASSRLS 角色绕过策略，表所有者通常也绕过。还需关注连接池租户上下文污染、策略组合及事务作用域。
缓存键若遗漏租户、用户授权范围或权限版本，可能复用别人的答案。命中时仍需授权验证，并处理撤权与删除失效。
把检索内容视为不可信数据，隔离指令与证据，限制工具权限，验证输出并持续红队测试。单句提示词无法保证彻底防御。
向量、缓存、索引和文件的物理清理可能异步完成。先提交不可读状态，检索时检查状态与版本，再重试清理并防止旧任务复活文档。
覆盖跨租户、显式拒绝、撤权、缓存命中、删除与并发时序测试，并结合审计、渗透测试和监控。测试通过不能证明绝对安全。''',
7:'''Rewrite 将原问题改写为更适合检索的表达；Multi-Query 产生多种检索表达并合并结果。两者都应防止偏离原意。
HyDE 用假设答案的向量帮助寻找相似证据，可能缓解短查询的语义不足。但假设答案不是事实，可能引入偏差与额外成本。
关键词检索擅长精确术语、编号与名称，向量检索擅长语义近似。混合可以互补，是否提升仍须按实际数据评测。
不同检索器分数尺度未必可比。RRF 按排名融合，降低标度校准需求，但丢失分数差距信息，融合参数仍需验证。
Bi-Encoder 分别编码查询与文档，适合预计算和大规模召回；Cross-Encoder 联合编码二者，通常更贵，适合候选集重排。
联合评估召回、重排延迟、模型成本与最终回答质量，选择收益开始递减的候选数量；不存在通用最佳 K。
长上下文中部信息有时较难被模型有效利用。表现随模型与任务变化，需测试证据位置、数量与上下文长度。
Packing 在 Token 预算内按相关性、去重、结构和证据覆盖组织内容；简单截断只保留前部，可能切断条款或遗漏关键证据。
Citation 表示回答指向何处，Groundedness 表示主张是否被证据支持。存在引用不代表引用正确或充分。
提高检索质量、校验权限与证据、要求引用、控制上下文并在证据不足时拒答，使用评测持续发现失败场景；不能保证消除所有幻觉。
限制缓冲区与在途任务，明确溢出策略；客户端断开时传播取消并关闭上游资源。响应式接口不自动解决阻塞或无限缓冲。
在代表性数据集上同时检验回答质量、安全、延迟、成本与失败恢复，满足预先定义的门槛后灰度验证。''',
8:'''在线人数是会话规模，并发是在同一时刻处于处理中的请求数。稳定条件下可用平均吞吐乘平均响应时间估算在途请求。
生成耗时长、输出持续占连接，模型 Token 吞吐与检索重排可能成为瓶颈，单看 QPS 会遗漏资源占用与长尾。
击穿是热点失效引发并发回源，穿透是查询不存在的数据持续回源，雪崩是大量缓存同时失效或缓存层故障。
Singleflight 通常合并同进程相同请求；分布式锁协调多个进程。需处理超时、租约、持有者校验与异常恢复。
虚拟线程降低阻塞等待的线程成本，不增加模型、数据库或 CPU 的容量。仍需限制在途请求并测量实际瓶颈。
JDBC 阻塞事件循环会拖慢其他请求。可使用受限线程池隔离阻塞调用或采用合适的响应式驱动，并监控队列。
慢客户端可能导致缓冲持续增长；断开后继续生成会浪费资源。需要有界队列、超时、溢出策略和上游取消。
不是。过大的连接池可能增加数据库竞争。根据数据库容量、事务耗时和等待指标压测选型，并设置超时。
限流控制进入速率，熔断暂时阻止调用故障依赖，舱壁隔离为不同依赖或业务分配独立资源预算。
TTFT 衡量首 Token 等待，TPOT 衡量后续 Token 间隔；P95/P99 是指定指标分布的长尾分位数，应明确统计对象。
普通压测常不覆盖流式连接、输出长度、Token 吞吐、取消和长尾。应使用真实查询分布与生成长度并记录各阶段指标。
先确定影响范围，再检查模型网关、检索、数据库、缓存和队列，结合 Trace 找关键路径，并排查变更、重试放大和资源饱和。''',
9:'''分层评估检索、上下文、生成、引用及安全，同时记录延迟和成本。离线黄金集与线上反馈互补，并设定上线门槛。
从真实任务与故障采样，覆盖难度、权限与拒答场景，明确标注规范、复核争议，并隔离训练、调参与测试数据。
Recall@K 是相关项中被前 K 项找回的比例；Precision@K 是前 K 项中相关项的比例。先定义相关性和去重单位。
Hit Rate 关心一次查询是否至少命中一项相关结果；Recall 关心相关结果找回了多少，二者不可互换。
MRR 强调首个相关结果出现的位置；nDCG 兼顾多项结果的分级相关性和排序。应明确截断 K 与理想排序集合。
Context Precision 关注上下文中的有效内容及排序；Context Recall 关注参考答案所需信息是否被覆盖。具体计算口径随指标实现而异。
Faithfulness 看答案是否受给定上下文支持，Correctness 看答案是否正确。错误证据也可能产生忠实但错误的回答。
相关性衡量是否回应问题，并不保证事实正确、证据充分或引用可靠。需要分别评估这些维度。
检查引用资源是否存在、定位是否准确、是否支持对应主张以及关键主张是否有充分引用，可结合人工抽检。
存在位置偏差、措辞偏差、自我偏好与不稳定性。应校准评分标准、使用人工对照并记录评测模型和版本。
不能。自动指标适合规模化筛查和回归，复杂事实、安全边界与争议样本仍需要人工复核。
在相同候选、查询和预算下做消融对比，观察排序与最终回答质量，以及延迟、成本和不同任务切片的退化。
A/B 随机分组比较方案效果；灰度逐步扩大曝光以控制风险。二者可结合，但灰度本身不保证因果可比。
大样本可能让很小的差异显著。还要看效应量、置信区间、成本、安全和业务价值，避免反复窥视与多重比较误判。
采集经过隐私处理的失败反馈，归因到检索、权限或生成等环节，审核进入数据集，迭代后做回归与灰度验证。'''}
for n,answers in banks.items():
 path=P/f'chapters/{n:02}.md';s=path.read_text(encoding='utf-8');start=s.rindex('模拟');end=s.find('\n## ',start)
 block=s[start:end];questions=re.findall(r'^\d+\\\. (.+)$',block,re.M);answers=answers.splitlines();assert len(questions)==len(answers),(n,len(questions))
 cards='<div class="review-bank">\n<p>先自行作答，再展开对照。参考答案为编辑补充，可结合本章正文深入阅读。</p>\n<button type="button" class="review-toggle">全部展开</button>\n'
 for i,(q,a) in enumerate(zip(questions,answers),1):cards+=f'<details class="review-card"><summary>{i}. {html.escape(q.replace(chr(92),""))}</summary><div class="review-answer"><p>{html.escape(a)}</p></div></details>\n'
 cards+='</div>\n';s=s[:start]+cards+s[end:]
 if n==6:
  s=re.sub(r'ACTIVE\n\n正常可检索\n\nDELETING\n\n立即禁止新的检索与内容读取\n\nPURGING\n\n异步清理向量、索引、缓存和文件\n\nDELETED\n\n完成删除与必要校验','| 状态 | 行为 |\n| --- | --- |\n| ACTIVE | 正常可检索 |\n| DELETING | 立即禁止新的检索与内容读取 |\n| PURGING | 异步清理向量、索引、缓存和文件 |\n| DELETED | 完成删除与必要校验 |',s)
  s=re.sub(r'(?m)^0([1-5])\n\n([^\n]+)\n\n([^\n]+)',lambda m:f'\n<div class="boundary-card"><span>0{m[1]}</span><div><strong>{m[2]}</strong><p>{m[3]}</p></div></div>\n',s)
 path.write_text(s,encoding='utf-8')
with (P/'assets/app.js').open('a',encoding='utf-8') as f:f.write("\ndocument.querySelectorAll('.review-toggle').forEach(button=>button.addEventListener('click',()=>{const cards=[...button.closest('.review-bank').querySelectorAll('details')];const open=cards.some(c=>!c.open);cards.forEach(c=>c.open=open);button.textContent=open?'全部收起':'全部展开';}));\n")
with (P/'assets/style.css').open('a',encoding='utf-8') as f:f.write('\n.review-bank{margin:24px 0}.review-card{border:1px solid var(--line);border-radius:10px;margin:12px 0;background:var(--paper)}.review-card summary{padding:18px 22px;cursor:pointer;font-weight:600;line-height:1.7}.review-card[open] summary{border-bottom:1px solid var(--line);color:var(--accent)}.review-answer{padding:4px 22px 12px}.review-toggle{padding:10px 18px;cursor:pointer}.boundary-card{display:flex;gap:22px;border:1px solid var(--line);border-radius:10px;padding:20px;margin:12px 0;background:var(--paper)}.boundary-card>span{color:var(--accent);font-size:1.4em}.boundary-card p{margin:8px 0 0} .review-card summary:focus-visible{outline:2px solid var(--accent)}\n')
