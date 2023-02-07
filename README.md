# 清宫造办处电子档案 Digital Records of Qing Manufacturing Office

这个项目用 OCR 技术识别清宫造办处档案, 并用全文搜索技术为学者提供方便的搜索能力.

This project employs Optical Character Recognition (OCR) to digitize historical records from the Qing manufacturing office. By utilizing full-text indexing and searching technology on the OCR results, it offers historians an efficient and convenient method to search through the digital records.

本项目原理如下图所示:

Here's an overview of how the project functions:


![Untitled Diagram](https://user-images.githubusercontent.com/109661872/214812125-2d6d62df-4543-4687-8250-92e0b63d2035.jpg)

其中, OCR 的工作通过 [古籍酷](https://gj.cool/) 提供的 OCR API 完成. 十分感谢古籍酷提供的 OCR 识别 API, 
大大加快了本项目的开发进度.

Thanks [gj.cool](https://gj.cool/) for their powerful OCR API, which greatly accelerated the development of this project.

## 内容 Content
由于清宫造办处档案数量十分庞大, 我计划分批完成电子档案的构建.

26/01/2023 更新:
  - 添加了 **49卷** 前 50 页内容

27/01/2023 更新:
  - 添加了 **49卷** 50 页至 96 页内容

28/01/2023 更新:
  - 添加了 **49卷** 96 页至 168 页内容

29/01/2023 更新:
  - 添加了 **49卷** 剩余部分
  - 添加了 **48卷** 前 127 页内容

30/01/2023 更新:
  - 添加了 **48卷** 剩余部分
  - 添加了 **44卷** 至 **47卷** 全部内容
  - 添加了 **43卷** 前 209 页内容

## 使用 Usage
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

### 运行

执行 `streamlit run app.py`，浏览器会自动打开搜索界面。输入关键字后按回车，系统将展示所有匹配结果。如果结果中 `XX 卷 XX 頁X半部分` 是超链接，单击可以打开 PDF 文件的对应页。（目前仅在 macOS + Chrome 环境下验证过，Chrome 需要安装 `Enable local file links` 插件）

Run `streamlit run app.py`. You should see a new pop-up on your browser. You can then input the keywords and press ENTER and the system will show you all the matches. If you want to see the original PDF page for context, just click the hyperlink in the results. (Works for macOS + Chrome. The Chrome plug `Enable local file links` is required)

![image](https://user-images.githubusercontent.com/109661872/217296951-d71e28f1-862b-4755-9e56-8a67dd516248.png)



#### 高级搜索 Advanced Search

目前支持输入以空格分隔的多个关键字，系统将会展示同时包含这些关键字的结果。

You can input space separated keywords for records that contains all of these keywords.

