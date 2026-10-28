"""Build the serial reader from maintained Markdown; no network access required."""
from pathlib import Path
import html, json, re, shutil, subprocess
import markdown
from pygments.formatters import HtmlFormatter

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'docs'
OUT.mkdir(exist_ok=True)
BOOK=json.loads((ROOT/'book.json').read_text(encoding='utf-8'))
NAMES=[c['title'] for c in BOOK['chapters']]
TOPICS=[c['topics'] for c in BOOK['chapters']]
COUNT=len(NAMES)
assert len(list((ROOT/'chapters').glob('[0-9][0-9].md')))==COUNT, 'Update book.json together with chapters/'

def page(title,body,chapter=0):
    menu=''.join(f'<a href="/{slug}/"'+(' aria-current="true"' if slug=='rag-empire-reader' else '')+f'>{name}</a>' for slug,name in [('pytorch-apprentice','PyTorch：炼金术士的学徒'),('ai-era-reader','AI 纪元'),('data-empire-reader','数据帝国'),('rag-empire-reader','RAG 帝国'),('system-design-reader','系统设计'), ('online-troubleshooting-reader', '生产环境'), ('coding-agent-reader', 'Agent 帝国'), ('interview-proof-reader', '面试官的审判')])
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark"><meta name="description" content="RAG 帝国：以 Java 后端工程师的视角，在小说和交互实验中理解RAG 工程。全书 {COUNT} 章，全书完结。"><title>{html.escape(title)} · RAG 帝国</title><script>try{{document.documentElement.dataset.theme=localStorage.getItem('rag-theme')||'white';document.documentElement.style.setProperty('--reader-size',Math.max(14,Math.min(26,Number(localStorage.getItem('rag-size'))||18))+'px')}}catch(e){{}}</script><link rel="stylesheet" href="style.css"><link rel="stylesheet" href="shelf-nav.css"><link rel="stylesheet" href="labs.css"><script src="app.js" defer></script><script src="labs.js" defer></script></head>
<body data-chapter="{chapter}" data-count="{COUNT}"><a class="skip" href="#main">跳到正文</a><div id="progress" aria-hidden="true"></div><header class="topbar"><a class="brand" href="index.html"><span class="emblem" aria-hidden="true">D<span>↗</span></span><span>RAG 帝国<small>THE RAG EMPIRE</small></span></a><nav class="shelf-nav" aria-label="学习项目导航"><a class="shelf-home" href="/">← 学习书架</a><details class="shelf-switch"><summary>切换项目 ▾</summary><div class="shelf-menu">{menu}</div></details></nav><div class="controls"><button id="search-open" aria-label="搜索全书">搜索 <kbd>/</kbd></button><button id="smaller" aria-label="缩小字号">A−</button><button id="larger" aria-label="增大字号">A＋</button><button id="theme" aria-label="切换背景：纯白、米白、深色">◐</button></div></header>
{body}<footer><a href="index.html">RAG 帝国</a><p>在故事中理解系统，在实验中观察原理。<span>全书 {COUNT} 章 · 全书完结</span></p><a href="https://github.com/wupzl/rag-empire-reader">项目源码 ↗</a></footer>
<dialog id="search-dialog" aria-labelledby="search-title"><div class="search-top"><h2 id="search-title">在帝国里寻找答案</h2><button id="search-close" aria-label="关闭搜索">关闭 ×</button></div><label for="query">关键词或代码，例如 Redis、背压、Checkpoint</label><input id="query" type="search" autocomplete="off" placeholder="搜索全书正文…"><p id="search-status" role="status">输入关键词，搜索 {COUNT} 章内容</p><div id="search-results"></div></dialog></body></html>'''

def render(source,toc=False):
    formulas=[]
    def stash(m):
        formulas.append({'tex':m[1] if m[1] is not None else m[2],'display':m[1] is not None})
        return f'MATHTOKEN{len(formulas)-1}END'
    chunks=re.split(r'(```.*?```|`[^`\n]+`)',source,flags=re.S)
    for i in range(0,len(chunks),2):
        chunks[i]=re.sub(r'\\\[(.*?)\\\]|\\\((.*?)\\\)',stash,chunks[i],flags=re.S)
    md=markdown.Markdown(extensions=['fenced_code','tables','toc','sane_lists','codehilite'],extension_configs={'toc':{'toc_depth':'2-2'},'codehilite':{'guess_lang':False}})
    rendered=md.convert(''.join(chunks))
    if formulas:
        run=subprocess.run(['node',str(ROOT/'render-math.cjs')],input=json.dumps(formulas),text=True,encoding='utf-8',capture_output=True,check=True)
        for i,value in enumerate(json.loads(run.stdout)): rendered=rendered.replace(f'MATHTOKEN{i}END',value)
    def fold_code(m):
        block=m[0]
        if block.count('\n') < 25: return block
        return '<details class="code-disclosure"><summary>展开代码 / 结构示例（较长）</summary>'+block+'</details>'
    rendered=re.sub(r'<div class="codehilite">.*?</div>',fold_code,rendered,flags=re.S)
    return rendered,md.toc

metadata=[]; search=[]
for i,path in enumerate(sorted((ROOT/'chapters').glob('[0-9][0-9].md'))):
    source=path.read_text(encoding='utf-8'); rendered,toc=render(source,True)
    title=NAMES[i]; minutes=max(5,round(len(source)/450))
    metadata.append({'number':i+1,'title':title,'topics':TOPICS[i],'minutes':minutes})
    booknav=''.join(f'<a class="{"current" if k==i else ""}" href="chapter-{k+1:02}.html"'+(' aria-current="page"' if k==i else '')+f'><span>{k+1:02}</span>{name}</a>' for k,name in enumerate(NAMES))
    nav=f'<a href="chapter-{i:02}.html">← 上一章<span>{NAMES[i-1]}</span></a>' if i else '<a href="index.html">← 全书目录<span>回到故事起点</span></a>'
    nav+=f'<a href="chapter-{i+2:02}.html">下一章 →<span>{NAMES[i+1]}</span></a>' if i<COUNT-1 else f'<a href="index.html">全书完 →<span>返回全书目录</span></a>'
    body=f'''<div class="reader-layout"><aside class="sidebar"><p class="eyebrow">THE EMPIRE’S JOURNEY</p><nav aria-label="全书章节">{booknav}</nav><details class="local-toc" open><summary>本章线索</summary>{toc}</details></aside><main id="main" class="chapter-main"><div class="chapter-heading"><p class="eyebrow">CHAPTER {i+1:02} <span>/ {COUNT:02} · 约 {minutes} 分钟</span></p><h1>{title}</h1><p class="topics">{TOPICS[i]}</p><div class="bridge">先遇见系统的问题，再理解技术为什么出现。</div></div><details class="mobile-toc"><summary>章节与本章目录</summary><nav aria-label="移动端章节">{booknav}</nav>{toc}</details><article>{rendered}</article><section class="practice"><h2>把原理放进实验</h2><p>调整参数，观察系统如何变化。所有实验均在当前浏览器中运行。</p><a href="practice.html">查看全部交互实验 →</a> · <a href="editorial.html">内容整理与技术校正 →</a></section><nav class="chapter-nav" aria-label="上下章">{nav}</nav></main></div>'''
    (OUT/f'chapter-{i+1:02}.html').write_text(page(title,body,i+1),encoding='utf-8')
    # Use actual rendered headings, including Unicode-safe anchors, as search boundaries.
    sections=re.split(r'(<h2 id="[^"]+">.*?</h2>)',rendered,flags=re.S)
    heading='故事开始'; anchor=''
    for section in sections:
        match=re.fullmatch(r'<h2 id="([^"]+)">(.*?)</h2>',section,flags=re.S)
        if match: anchor=match[1]; heading=html.unescape(re.sub('<[^>]+>','',match[2])); continue
        text=html.unescape(re.sub('<[^>]+>',' ',section))
        search.append({'chapter':i+1,'title':title,'section':heading,'url':f'chapter-{i+1:02}.html'+('#'+anchor if anchor else ''),'text':re.sub(r'\s+',' ',text)})

cards=''.join(f'<a class="chapter-card" href="chapter-{i+1:02}.html"><span class="chapter-number">{i+1:02}</span><div><h3>{item["title"]}</h3><p>{item["topics"]}</p></div><span>约 {item["minutes"]} 分钟 →</span></a>' for i,item in enumerate(metadata))
home=f'''<main id="main" class="home"><section class="hero"><div class="hero-copy"><p class="eyebrow">THE RAG EMPIRE / ENGINEERING ARCHIVES</p><h1>让每一个答案，<br>都有<span>证据。</span></h1><p class="hero-subtitle">RAG 帝国：从实验室到生产战场</p><p class="intro">一场三百万的幻觉事故，一座知识帝国的诞生。<br>跟随林川，从第一份文档走向可信的生产系统。</p><div class="hero-actions"><a class="primary" href="chapter-01.html">开启第一章 →</a><a id="resume" hidden href="chapter-01.html">继续阅读 →</a></div><p class="hero-note">九章完结 · 本地交互实验 · 无需登录</p></div><div class="book-art" aria-hidden="true"><div class="orbit orbit-one"></div><div class="book"><p>ENGINEERING<br>THE EVIDENCE</p><div class="book-title">RAG 帝国<span>从实验室到生产战场</span></div><div class="book-symbol">R<span>RETRIEVE → VERIFY → ANSWER</span></div><div class="book-bottom">知识 · 权限 · 证据<span>ARCHIVE 01—09</span></div></div></div></section><section class="catalog"><div class="catalog-heading"><h2>帝国工程档案</h2><a href="practice.html">进入交互实验室 ↗</a></div>{cards}</section><section class="reading-note"><h2>阅读说明</h2><p>完整九章，按工程问题顺序阅读。示例不调用在线模型。主题、字号和阅读进度保存在当前浏览器。</p><a href="editorial.html">技术校正与参考来源 →</a></section></main>'''
(OUT/'index.html').write_text(page('全书目录',home),encoding='utf-8')
for name,title,source in [('practice','交互实验室',(ROOT/'LABS.md').read_text(encoding='utf-8')),('editorial','技术校正与来源',(ROOT/'EDITORIAL.md').read_text(encoding='utf-8'))]:
    body,_=render(source)
    (OUT/f'{name}.html').write_text(page(title,f'<main id="main" class="standalone"><a href="index.html">← 返回目录</a><article>{body}</article></main>'),encoding='utf-8')
(OUT/'search.json').write_text(json.dumps(search,ensure_ascii=False),encoding='utf-8')
(OUT/'chapters.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'syntax.css').write_text(HtmlFormatter().get_style_defs('.codehilite'),encoding='utf-8')
for path in (ROOT/'assets').iterdir():
    if path.is_file(): shutil.copyfile(path,OUT/path.name)
(OUT/'.nojekyll').touch()
print(f'Built {len(metadata)} chapters, 5 interactive labs and 3 supporting pages.')
