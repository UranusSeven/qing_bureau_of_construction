# 清宫造办处电子档案 Digital Records of Qing Manufacturing Office

This project employs Optical Character Recognition (OCR) to digitize historical records from the Qing manufacturing office. By utilizing full-text indexing and searching technology on the OCR results, it offers historians an efficient and convenient method to search through the digital records.

这个项目用 OCR 技术识别清宫造办处档案, 并用全文搜索技术为学者提供方便的搜索能力.

Here's an overview of how the project functions:

本项目原理如下图所示:


![Untitled Diagram](https://user-images.githubusercontent.com/109661872/214812125-2d6d62df-4543-4687-8250-92e0b63d2035.jpg)

Thanks [gj.cool](https://gj.cool/) for their powerful OCR API, which greatly accelerated the development of this project.

其中, OCR 的工作通过 [古籍酷](https://gj.cool/) 提供的 OCR API 完成. 十分感谢古籍酷提供的 OCR 识别 API, 
大大加快了本项目的开发进度.


## 内容
由于清宫造办处档案数量十分庞大, 我计划分批完成电子档案的构建。

26/01/2023 更新:
  - 添加了 **49卷** 前 50 页内容

27/01/2023 更新:
  - 添加了 **49卷** 50 页至 96 页内容

## 使用
### 克隆本项目 Clone the Project
SSH:
```
git clone git@github.com:UranusSeven/qing_bureau_of_construction.git
```

HTTPS:
```
git clone https://github.com/UranusSeven/qing_bureau_of_construction.git
```

### 安装依赖 Install Dependencies

为了避免依赖版本冲突，强烈**建议创建新的虚拟环境**. 之后可以通过 `pip` 安装依赖.

To avoid conflicts, it is highly recommended to create a new virtual environment before installing the dependencies. You can then install the dependencies with `pip`.

```
pip install -r requirements.txt
```

### 执行 `search.py` 并按提示进行使用 Execute `search.py` and Follow the Instructions

![render1674801085308](https://user-images.githubusercontent.com/109661872/215024151-8f2b1753-fc04-47bf-8905-54dc92b0a718.gif)

Select the page you want and press `enter`, the system will open the page for you.

我们选中想要查看的页，点击回车，系统将自动打开这一页.

#### 高级搜索 Advanced Search

我们可以使用 `AND`, `OR`, 'NOT' 与关键字进行组合, 规则见 whoosh 的[文档](https://whoosh.readthedocs.io/en/latest/querylang.html). 如 `法瑯 AND 銅瓶` 将会返回同时包含这两个关键字的文档.

You can combine `AND`, `OR`, 'NOT' with your key words according to [whoosh's query language](https://whoosh.readthedocs.io/en/latest/querylang.html).

![render1674802568386](https://user-images.githubusercontent.com/109661872/215027514-f1d48dce-74b9-4690-8fb2-45353e511580.gif)

