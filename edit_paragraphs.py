"""Consolidate prose while retaining all original words and speaker turns."""
from pathlib import Path
import re,json
P=Path(__file__).parent
stats=[]
def prose(x):
 return bool(x) and '\n' not in x and not re.match(r'[#<>|\[\d`*\-\\]',x) and not re.fullmatch(r'[A-Za-z0-9_ /→+.,:：%()—]+',x)
def dialogue(x):return x.startswith('“') and x.endswith('”')
def attribution(x):return bool(re.search(r'(?:问|回答|说道|解释|强调|提醒|补充|反问|继续说|提出|写下)[：。]$',x)) and len(x)<55
for path in sorted((P/'chapters').glob('*.md')):
 s=path.read_text(encoding='utf-8');before=s
 # Protect code and authored HTML as complete blocks before editing prose.
 tokens={}
 def protect(m):
  key=f'@@PROTECTED{len(tokens)}@@';tokens[key]=m[0];return '\n\n'+key+'\n\n'
 s=re.sub(r'```.*?```|<(div|ol|details)\b[^>]*>.*?</\1>',protect,s,flags=re.S)
 blocks=[x.strip() for x in re.split(r'\n\s*\n',s) if x.strip()];out=[];merged=0
 for block in blocks:
  if out and prose(block) and prose(out[-1]) and not dialogue(block) and not dialogue(out[-1]) and not attribution(out[-1]) and not attribution(block) and not out[-1].endswith(('：',':')) and len(out[-1])+len(block)<=260:
   out[-1]+=block;merged+=1
  elif out and dialogue(block) and attribution(out[-1]):
   out[-1]='**'+out[-1]+'** '+block;merged+=1
  elif out and (dialogue(block) or block.startswith('> ')) and re.fullmatch(r'(?:客户|用户|AI 客服|模型|模型回答|原始问题|用户问题|系统回答|证据内容|检索结果)[：:]',out[-1]):
   out[-1]='**'+out[-1]+'**\n\n'+block
  else:out.append(block)
 s='\n\n'.join(out)+'\n'
 for key,value in tokens.items():s=s.replace(key,value)
 # Preserve exact content apart from whitespace and inserted emphasis.
 norm=lambda x:re.sub(r'\s|\*\*','',x)
 assert norm(s)==norm(before),path
 path.write_text(s,encoding='utf-8');stats.append({'chapter':path.stem,'paragraph_breaks_removed':merged})
(P/'PARAGRAPH_REVIEW.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
print(stats)
