
# 财务报表分析系统

## 简介
本项目是一个基于 Flask 的 Web 应用程序，旨在实现对财务报表 PDF 文件的解析和分析。通过调用 Textin OCR API 将 PDF 财报文件转换为 Markdown 格式，再使用 OpenAI 的 DeepSeek 模型进行深度财务分析，最终将分析结果以 HTML 格式返回给用户。

## 功能特点
- **文件上传**：支持用户上传 PDF 格式的财务报表文件。
- **OCR 解析**：利用 Textin OCR API 将 PDF 文件转换为 Markdown 格式的文本数据。
- **财务分析**：使用 OpenAI 的 DeepSeek 模型对解析后的财务数据进行专业分析，包括风险点、增长亮点和估值建议。
- **结果展示**：将分析结果以 HTML 格式返回给用户，方便查看和展示。

## 安装与配置
### 环境要求
- Python 3.x
- Flask
- requests
- pandas
- openai
- markdown

### 安装依赖
在项目根目录下，执行以下命令安装所需的 Python 依赖：
```bash
pip install flask requests pandas openai markdown
```

### 配置 API 密钥
在 `app.py` 文件中，配置 Textin OCR 和 OpenAI 的 API 密钥：
```python
# 初始化 API 客户端
textin_client = TextinOcr(
    app_id="971357873************42beff5c",
    app_secret="2d5b5b6*****************061dbe26a0"
)

deepseek_client = FinancialAnalyst(
    api_key="sk-k3k2jeBWSD7pEcLMMHTeHdAxmrw7DC5z78XharBWnYAJHneI"
)
```
请将上述密钥替换为你自己的有效密钥。

## 使用方法
### 启动应用
在项目根目录下，执行以下命令启动 Flask 应用：
```bash
python app.py
```

### 访问应用
打开浏览器，访问 `http://127.0.0.1:5000`，即可看到应用的首页。

### 上传文件并分析
在首页选择要上传的 PDF 格式的财务报表文件，点击上传按钮，系统将自动进行文件解析和财务分析，并将分析结果以 HTML 格式展示在页面上。

## 注意事项
- 请确保你的 API 密钥有效，否则可能会导致 API 请求失败。
- 本应用仅支持上传 PDF 格式的文件，其他格式的文件将被拒绝。
- 由于使用了第三方 API，可能会受到网络延迟和 API 调用限制的影响，请耐心等待分析结果。

## 日志记录
应用的日志信息将记录在 `financial_analysis.log` 文件中，方便后续查看和调试。

## 贡献与反馈
如果你在使用过程中遇到问题或有任何建议，请随时提交 Issue 或 Pull Request。

## 许可证
本项目采用 [MIT 许可证](LICENSE) 进行授权。
