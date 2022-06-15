# ReceiptInfoExtract
A tool to extract information from receipt in pdf. 一个用于提取pdf格式发票中的内容的工具

## 特性

+ 提取：
    + 中文的pdf格式发票中的商品总额
    + 中文的pdf格式发票中的商品名称信息以及对应的购买数量
+ 支持特点：
    + 支持商品详情在后续清单中的分页发票
    + 根据发票中的表头等固定信息提取商品名称以及数量的相对位置，可以适应不同省份的发票格式
+ 扩展：
    + 可以根据需要去扩展提取发票中的其他内容


## 工具依赖

本文依赖[pdf2json](https://github.com/modesty/pdf2json)工具，将pdf格式的发票生成json格式的文字识别结果，将json格式的发票识别结果输入到本工具中可以在命令行以及文件中存储。其他python的依赖都是常见的，不过多赘述。

## 使用方法

修改入口main函数中存储json格式发票文件的文件夹路径，直接分析即可。