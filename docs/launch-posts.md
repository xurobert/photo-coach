# 发布短帖（冲 10 star）

## V2EX（分享创造）

标题：做了个免费本地挑图工具 Photo Coach：去重选片 + 中文模糊搜旧片 + 拍摄趋势建议

正文：
拍 cos / 风景 / 花卉的时候最烦两件事：连拍一堆不知道留哪张，以及「记得有张雨天红伞」在硬盘里翻半天。

我开源了一个本地工具 Photo Coach（MIT）：
- 文件夹扫描 → 近重复去重，按清晰度/曝光建议保留
- 启发式打分（默认不用云端模型）
- 中文模糊检索旧片
- 根据 EXIF 给可执行的趋势建议（焦段/光圈/时段）

不算 Lightroom 替代品，修图仍用你现在的软件；它补的是「选片 + 找回 + 回顾进步」这一段。

仓库：https://github.com/xurobert/photo-coach

```bash
pip install -e .
photo-coach demo
```

欢迎试用提 issue。目标先老实拿到 10 个 star，把演示和真实样片补齐。

---

## X / 摄影号短帖

拍完一堆最崩溃的不是不会修，是：
1）连拍留哪张
2）记得有张「雨天红伞」却翻不到

开源了个本地小工具 Photo Coach：
去重选片 + 打分 + 中文模糊搜旧片 + 拍摄趋势建议
免费，可不上云

https://github.com/xurobert/photo-coach

`photo-coach demo` 就能跑。摄影朋友试用反馈欢迎来砸。
