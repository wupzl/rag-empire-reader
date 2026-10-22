(() => {
'use strict';
const configs={acl:[['用户租户','alpha'],['文档租户','alpha'],['用户角色','reader'],['允许角色','reader'],['已授权（1 是 / 0 否）','1']],cost:[['请求数',10000],['每请求输入 Token',2000],['每请求输出 Token',400],['输入单价',1],['输出单价',4]],capacity:[['每秒请求数',20],['平均响应秒数',5],['每实例 QPS',10],['目标利用率（%）',70],['模型总输出 Token/秒',2000],['每请求输出 Token',400]],ranking:[['相关性等级','3,0,2,1,0'],['全库相关文档数',5]],ab:[['A 用户数',1000],['A 成功数',100],['B 用户数',1000],['B 成功数',120]]};
for(const el of document.querySelectorAll('[data-lab]')){
 const key=el.dataset.lab,inputs=[];
 for(const [name,value] of configs[key]||[]){const label=document.createElement('label');label.append(name+' ');const input=document.createElement('input');input.value=value;input.type=typeof value==='number'?'number':'text';if(input.type==='number'){input.min='0';input.step='any'}label.append(input);el.append(label);inputs.push(input)}
 const output=document.createElement('output');output.setAttribute('aria-live','polite');el.append(output);
 const update=()=>{try{const values=inputs.map(x=>x.value.trim()),n=values.map(Number);let result;
 if(values.some(x=>!x))throw Error('请填写所有字段');
 if(key==='acl')result=values[0]===values[1]&&values[2]===values[3]&&values[4]==='1'?'允许访问：租户、角色和授权均通过。':'拒绝访问：至少一项条件不满足。';
 else if(key==='ranking'){const r=values[0].split(',').map(x=>Number(x.trim()));if(r.some(x=>!Number.isInteger(x)||x<0||x>3)||!Number.isInteger(n[1])||n[1]<r.filter(x=>x>0).length||n[1]<1)throw Error('等级须为 0—3 的整数，总相关数须为正整数且覆盖命中项');const hit=r.filter(x=>x>0).length,dcg=a=>a.reduce((s,g,i)=>s+(2**g-1)/Math.log2(i+2),0),ideal=dcg([...r].sort((a,b)=>b-a));result=`Precision@${r.length}: ${(hit/r.length).toFixed(3)}\nRecall: ${(hit/n[1]).toFixed(3)}\nMRR: ${r.findIndex(x=>x>0)<0?0:(1/(r.findIndex(x=>x>0)+1)).toFixed(3)}\nnDCG（列表内理想）: ${ideal?(dcg(r)/ideal).toFixed(3):0}`}
 else{if(n.some(x=>!Number.isFinite(x)||x<0))throw Error('请输入有限的非负数字');if(key==='cost')result=`总成本：$${(n[0]*(n[1]*n[3]+n[2]*n[4])/1e6).toFixed(4)}`;
 if(key==='capacity'){if(n[2]<=0||n[3]<=0||n[3]>100||n[5]<=0)throw Error('容量与输出 Token 须大于零，利用率须在 (0,100]');result=`平均在途请求：${(n[0]*n[1]).toFixed(1)}\n实例数量：${Math.ceil(n[0]/(n[2]*n[3]/100))}\n模型理想上界：${(n[4]/n[5]).toFixed(2)} 请求/秒`}
 if(key==='ab'){const[a,x,b,y]=n;if(!n.every(Number.isInteger)||!a||!b||x>a||y>b)throw Error('用户数须为正整数，成功数不可超过用户数');const p=(x+y)/(a+b),se=Math.sqrt(p*(1-p)*(1/a+1/b));if(Math.min(a*p,a*(1-p),b*p,b*(1-p))<5||!se)throw Error('样本不足以进行正态近似判断');const z=(y/b-x/a)/se;result=`B−A：${((y/b-x/a)*100).toFixed(2)} 个百分点\nz：${z.toFixed(3)}\n${Math.abs(z)>1.96?'达到约 5% 双侧显著性水平':'未达到约 5% 双侧显著性水平'}`}}
 output.textContent=result;
 }catch(e){output.textContent=e.message}};
 el.addEventListener('input',update);const reset=document.createElement('button');reset.textContent='重置实验';reset.onclick=()=>{inputs.forEach((x,i)=>x.value=configs[key][i][1]);update()};el.append(reset);update();
}
})();
