# 帝国交互实验室

修改参数即可更新结果。全部在浏览器本地计算，不上传数据。

## 权限门禁
同时验证租户、角色与文档授权。此处是规则教学模型。
<div class="lab" data-lab="acl"></div>

## Token 成本预算
单价单位为美元 / 百万 Token，由你自行填写。
<div class="lab" data-lab="cost"></div>

## 并发与容量
Little 定律适用于稳定系统的长期均值；模型吞吐量为理想上界。
<div class="lab" data-lab="capacity"></div>

## 排序评测
输入检索结果的相关性等级，逗号分隔，0 表示无关。相关文档总数必须不少于已检出的相关项。nDCG 的理想排序按此检索列表重排，非全库理想排序。
<div class="lab" data-lab="ranking"></div>

## A/B 实验
独立用户、固定样本量的双侧双比例 z 检验。显示差值与 z 值；|z| 大于 1.96 对应约 5% 显著性水平。显著不代表有业务价值。小样本或期望成功/失败数不足 5 时不作判断。
<div class="lab" data-lab="ab"></div>
