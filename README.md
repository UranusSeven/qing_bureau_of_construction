# 清宫造办处电子档案 Digital Records of Qing Bureau of Construction

这个项目用 OCR 技术识别清宫造办处档案, 并用全文搜索技术为学者提供方便的搜索能力.

本项目原理如下图所示:


![Untitled Diagram](https://user-images.githubusercontent.com/109661872/214812125-2d6d62df-4543-4687-8250-92e0b63d2035.jpg)


其中, OCR 的工作通过 [古籍酷](https://gj.cool/) 提供的 OCR API 完成. 十分感谢古籍酷提供的 OCR 识别 API, 大大加快了本项目的开发进度.


## 使用
如果没有重新构建索引的需求, 直接 clone 本项目, 执行 `search.py`, 按照提示使用即可.

### clone 本项目
using ssh:
```
git clone git@github.com:UranusSeven/qing_bureau_of_construction.git
```

using https:
```
git clone https://github.com/UranusSeven/qing_bureau_of_construction.git
```
