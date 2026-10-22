"""Publish with existing Git Credential Manager credentials; never print secrets."""
import subprocess,json,urllib.request,urllib.error
from pathlib import Path
root=Path(__file__).resolve().parent
cred=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\n\n',capture_output=True,text=True,check=True)
fields=dict(line.split('=',1) for line in cred.stdout.splitlines() if '=' in line)
token=fields.get('password')
if not token:raise SystemExit('No GitHub credential available')
def api(path,data=None,method=None):
 req=urllib.request.Request('https://api.github.com/'+path,data=json.dumps(data).encode() if data is not None else None,method=method,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
 try:
  with urllib.request.urlopen(req) as r:return json.load(r)
 except urllib.error.HTTPError as e:
  if e.code==404:return None
  raise RuntimeError(f'GitHub API returned {e.code}: {e.read().decode()[:300]}') from None
if not api('repos/wupzl/rag-empire-reader'):api('user/repos',{'name':'rag-empire-reader','private':False,'description':'RAG 帝国：从实验室到生产战场 · 小说式工程阅读与交互实验'})
def git(*args):subprocess.run(['git',*args],cwd=root,check=True)
if not (root/'.git').exists():git('init','-b','main');git('remote','add','origin','https://github.com/wupzl/rag-empire-reader.git')
git('add','.');git('commit','-m','Build RAG Empire reader with interactive engineering labs');git('push','-u','origin','main')
if not api('repos/wupzl/rag-empire-reader/pages'):api('repos/wupzl/rag-empire-reader/pages',{'source':{'branch':'main','path':'/docs'}},'POST')
print('GitHub repository pushed; Pages configured.')
