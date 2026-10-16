# -*- coding: utf-8 -*-
"""生成完全自包含的单文件离线页面 offline.html（内联数据/样式/脚本，手机可离线打开）"""
import json, io, os

BASE = os.path.dirname(os.path.abspath(__file__))

with io.open(os.path.join(BASE, 'data.json'), encoding='utf-8') as f:
    data = json.load(f)

ai = data['ai_news']
tech = data['tech_news']
date = data['date']

HTML = u'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#131722">
<title>一人公司工作台 · 每日知识</title>
<style>
:root{--bg:#f5f6f8;--card:#fff;--txt:#1a1e29;--txt2:#6b7280;--line:#eceef2;--ai:#4f6bff;--tech:#00b578;--dark:#131722}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{background:var(--bg);color:var(--txt);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;padding-bottom:calc(16px + env(safe-area-inset-bottom))}
.header{background:linear-gradient(135deg,#131722,#2a3550);color:#fff;padding:26px 18px 58px}
.header .hd-top{display:flex;align-items:center;justify-content:space-between}
.header .logo{font-size:19px;font-weight:800}
.header .date{font-size:12px;color:#aab2c5;margin-top:4px}
.header .big{font-size:26px;font-weight:800;margin-top:14px}
.header .sub{font-size:13px;color:#aab2c5;margin-top:5px}
.tabs{display:flex;gap:8px;margin:-34px 18px 0;position:relative;z-index:2}
.tab{flex:1;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:13px 0;text-align:center;font-size:14px;font-weight:700;color:var(--txt2);cursor:pointer;box-shadow:0 4px 14px rgba(19,23,34,.06)}
.tab.on{color:#fff}
.tab.on.ai{background:var(--ai);border-color:var(--ai)}
.tab.on.tech{background:var(--tech);border-color:var(--tech)}
.tab small{display:block;font-size:11px;font-weight:400;opacity:.75;margin-top:2px}
.list{padding:14px 16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:15px 16px;margin-bottom:11px;display:flex;gap:12px;align-items:flex-start;animation:up .35s ease}
@keyframes up{from{transform:translateY(10px);opacity:0}to{transform:none;opacity:1}}
.card .idx{width:26px;height:26px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:800;color:#fff;flex-shrink:0}
.card.ai .idx{background:var(--ai)}
.card.tech .idx{background:var(--tech)}
.card .body{flex:1}
.card .t{font-size:15px;font-weight:750;margin-bottom:4px}
.card .s{font-size:13px;color:var(--txt2);line-height:1.6}
.foot{text-align:center;color:#b0b6c2;font-size:12px;padding:8px 16px 4px}
.tip{margin:0 16px;background:#fff7e6;border:1px solid #ffd591;color:#8a5a00;border-radius:12px;padding:12px 14px;font-size:12.5px;line-height:1.6}
</style>
</head>
<body>
<div class="header">
  <div class="hd-top">
    <div>
      <div class="logo">一人公司工作台</div>
      <div class="date">''' + date + u'''</div>
    </div>
  </div>
  <div class="big">每日基础知识</div>
  <div class="sub">AI 基础 + 计算机基础 · 每天轮换新内容</div>
</div>

<div class="tabs">
  <div class="tab on ai" data-tab="ai">AI 基础<small>''' + str(len(ai)) + u''' 条</small></div>
  <div class="tab tech" data-tab="tech">计算机基础<small>''' + str(len(tech)) + u''' 条</small></div>
</div>

<div class="list" id="list"></div>

<div class="tip">💡 <b>添加到主屏幕</b>：iPhone 用 Safari 打开，点分享 →「添加到主屏幕」；安卓用 Chrome，点 ⋮ 菜单 →「安装应用」。之后像 App 一样一键打开，无需联网加载页面。</div>
<div class="foot">一人公司工作台 · 每日自动更新</div>

<script>
var DATA = __DATA__;
var cur = 'ai';
function render(tab){
  var arr = tab === 'ai' ? DATA.ai_news : DATA.tech_news;
  var cls = tab === 'ai' ? 'ai' : 'tech';
  var html = '';
  for(var i=0;i<arr.length;i++){
    var it = arr[i];
    html += '<div class="card '+cls+'" style="animation-delay:'+(i*0.03)+'s">'
      + '<div class="idx">'+(i+1)+'</div>'
      + '<div class="body"><div class="t">'+it.title+'</div><div class="s">'+it.summary+'</div></div>'
      + '</div>';
  }
  document.getElementById('list').innerHTML = html;
}
document.querySelectorAll('.tab').forEach(function(t){
  t.addEventListener('click', function(){
    cur = t.getAttribute('data-tab');
    document.querySelectorAll('.tab').forEach(function(x){x.classList.remove('on')});
    t.classList.add('on');
    render(cur);
  });
});
render('ai');
</script>
</body>
</html>
'''

HTML = HTML.replace('__DATA__', json.dumps(data, ensure_ascii=False))

out = os.path.join(BASE, 'offline.html')
with io.open(out, 'w', encoding='utf-8') as f:
    f.write(HTML)

print('已生成 offline.html（AI %d 条 / 计算机 %d 条，日期 %s）' % (len(ai), len(tech), date))
