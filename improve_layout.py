"""One-time, reviewed source migration. Build output remains reproducible."""
from pathlib import Path
import re,html,json
P=Path(__file__).parent
report=[]
def table(s,start,end,headers,width):
 a=s.index(start)+len(start);b=s.index(end,a);raw=s[a:b];items=[x.strip() for x in raw.strip().split('\n\n') if x.strip()]
 assert len(items)%width==0,(start,items)
 rows=[items[i:i+width] for i in range(0,len(items),width)]
 out='\n\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*width)+' |\n'+''.join('| '+' | '.join(x.replace('|',' / ').replace('\n',' ') for x in row)+' |\n' for row in rows)+'\n'
 report.append(start);return s[:a]+out+s[b:]
def flow(s,start,end):
 a=s.index(start)+len(start);b=s.index(end,a);items=[x.strip() for x in s[a:b].strip().split('\n\n') if x.strip()]
 assert all('\n' not in x and not x.startswith('“') for x in items),(start,items)
 out='\n\n<ol class="engineering-flow">'+''.join('<li>'+html.escape(x)+'</li>' for x in items)+'</ol>\n\n';report.append(start);return s[:a]+out+s[b:]
for n in range(1,10):
 path=P/f'chapters/{n:02}.md';s=path.read_text(encoding='utf-8')
 # Numeric dashboard values are not chapter headings.
 s=re.sub(r'^## ([$\d][^\n]*)$',r'<p class="metric-value">\1</p>',s,flags=re.M)
 if n==2:
  a=s.index('用户入口');b=s.index('陈默盯着架构图',a)
  s=s[:a]+'''| 层次 | 组件 / 链路 |
| --- | --- |
| 用户入口 | Vue 3 · API Gateway · Spring Security / JWT |
| 知识入库 | 文件上传与校验 → 解析 / OCR / 结构识别 → Heading Path 分块 → Embedding 向量化 → PostgreSQL + pgvector |
| 在线问答 | Query 理解 / 改写 → Hybrid Search 混合检索 → Rerank 重排序 → 上下文构造 / LLM → SSE 流式回答 + 引用 |
| 生产能力 | 权限隔离 · Redis · 消息队列 · 可观测性 · 评测 · 灰度 · 审计 |

'''+s[b:];report.append('总体架构：按实际链路分组')
 if n==3:
  s=flow(s,'林川设计了如下状态：','“注意，”')
  s=table(s,'运维负责人带来一份数据统计。','以上为小说设定',['指标','数值','单位'],3)
 if n==6:
  s=flow(s,'错误的主流程：全局 Top K 后过滤','目标流程：在检索查询中强制权限约束')
  s=flow(s,'目标流程：在检索查询中强制权限约束','“但是 PostgreSQL')
 if n==7:
  s=table(s,'示例：32,000 Token 的请求预算','仅为预算示例',['预算项目','Token'],2)
  s=flow(s,'林川在白板上画出两条检索通道。','“我们为什么不直接')
  s=flow(s,'Bi-Encoder：分别编码','向量可以提前计算')
  s=flow(s,'Cross-Encoder：联合编码','能够建模 Query')
 if n==8:
  s=s.replace('0 s8 s16 s24 s32 sP50P90P95P99','> 原稿此处仅保留坐标轴标签，未提供可恢复的各分位数数值，因此省略图表。下方阶段耗时用于说明关键路径，不能替代分位数数据。')
 if n==9:
  s=table(s,'示例：分阶段扩大新版本流量','仅为示例阶段',['阶段','流量比例','验证重点'],3)
  s=table(s,'### 一条自动化评测流水线','### 一个简化的 Python',['环节','职责'],2)
  s=table(s,'### 数据闭环如何工作？','新样本持续反馈到下一轮质量改进',['环节','工作内容'],2)
 # Fix numbered subheadings accidentally flattened to h2 in the source.
 if n in [8,9]:s=re.sub(r'^## (\d+\. )',r'### \1',s,flags=re.M)
 path.write_text(s,encoding='utf-8')
(P/'LAYOUT_REVIEW.md').write_text('# 全书阅读排版检查\n\n九章均检查了标题、正文、代码、表格和技术清单。保留叙事段落；结构化内容按语义整理，缺失图表数据不补造。\n\n'+ '\n'.join('- '+x for x in report),encoding='utf-8')
