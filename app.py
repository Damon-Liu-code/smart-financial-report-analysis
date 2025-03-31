# -*- coding: utf-8 -*-

# app.py
from flask import Flask, render_template, request, jsonify
import os
import json
from werkzeug.utils import secure_filename
import requests
import pandas as pd
from openai import OpenAI
import logging
from datetime import datetime
import markdown
import re

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

class TextinOcr(object):
    def __init__(self, app_id, app_secret):
        self._app_id = app_id
        self._app_secret = app_secret
        self.host = 'https://api.textin.com'

    def recognize_pdf2md(self, image_path, options, is_url=False):
        """
        pdf to markdown
        :param options: request params
        :param image_path: string
        :param is_url: bool
        :return: response

        options = {
            'pdf_pwd': None,
            'dpi': 144,  # 设置dpi为144
            'page_start': 0,
            'page_count': 1000,  # 设置解析的页数为1000页
            'apply_document_tree': 0,
            'markdown_details': 1,
            'page_details': 0,  # 不包含页面细节信息
            'table_flavor': 'md',
            'get_image': 'none',
            'parse_mode': 'scan',  # 解析模式设为scan
        }
        """
        url = self.host + '/ai/service/v1/pdf_to_markdown'
        headers = {
            'x-ti-app-id': self._app_id,
            'x-ti-secret-code': self._app_secret
        }
        if is_url:
            image = image_path
            headers['Content-Type'] = 'text/plain'
        else:
            image = get_file_content(image_path)
            headers['Content-Type'] = 'application/octet-stream'

        return requests.post(url, data=image, headers=headers, params=options)

class FinancialAnalyst:
    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://tbnx.plus7.plus/v1",
        )

    def analyze_financials(self, financial_data):
        """
        执行深度财务分析（使用官方SDK）
        """
        prompt = f"""你是一位顶级证券分析师，请根据以下财务数据进行专业分析： {financial_data}

        要求用中文输出：
        1. 三个最重要的风险点（用🚨标记）
        2. 三个最突出的增长亮点（用💡标记） 
        3. 估值建议（用📈标记）
        格式要求：Markdown列表，每个分类最多3条"""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system", "content": "你是拥有20年经验的证监会持牌财务分析师，擅长发现数据背后的商业逻辑"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ 分析失败：{str(e)}"
    
    def analyze_echarts_data(self, financial_data):
        """
        执行深度财务分析获得图表
        """
        prompt = f"""你是一位顶级证券分析师，请根据以下财务数据进行专业分析： {financial_data}

        要求用中文输出：
        1. 三个最重要的风险点（用🚨标记）
        2. 三个最突出的增长亮点（用💡标记） 
        3. 估值建议（用📈标记）
        格式要求：Markdown列表，每个分类最多3条"""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system", "content": "你是拥有20年经验的证监会持牌财务分析师，擅长发现数据背后的商业逻辑"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ 分析失败：{str(e)}"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 16MB

# 初始化API客户端
textin_client = TextinOcr(
    app_id="971357873d*******842bef0f5c",
    app_secret="2d5b5b62677****061dbdde26a0"
)

deepseek_client = FinancialAnalyst(
    api_key="sk-k3k2jeBWSD7pEcL*******7DC5z78XharBWnYAJHneI"
)

# 配置日志（在Flask应用初始化后添加）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('financial_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    start_time = datetime.now()
    filepath = None
    try:
        # ========== 1. 接收文件 ========== 
        logger.info("收到分析请求 | Headers: %s", request.headers)
        
        file = request.files.get('file')
        if not file:
            logger.error("未接收到文件")
            return jsonify(error="请选择要上传的文件"), 400
            
        if not file.filename.lower().endswith('.pdf'):
            logger.error("文件类型错误: %s", file.content_type)
            return jsonify(error="仅支持PDF文件"), 400

        # ========== 2. 保存文件 ========== 
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logger.info("文件暂存成功 | 路径: %s | 大小: %dKB", 
                   filepath, os.path.getsize(filepath)//1024)

        # ========== 3. 解析财报 ========== 
        logger.info("开始解析财报...")
        
        resp = textin_client.recognize_pdf2md(filepath, {
            'page_start': 0,
            'page_count': 1000,  # 设置解析页数为1000页
            'table_flavor': 'md',
            'parse_mode': 'scan',  # 设置解析模式为scan模式
            'page_details': 0,  # 不包含页面细节
            'markdown_details': 1,
            'apply_document_tree': 1,
            'dpi': 144  # 分辨率设置为144 dpi
        })
        logger.info("request time: %s", resp.elapsed.total_seconds())

        financial_data = json.loads(resp.text)['result']['markdown']
        
        # 记录解析后的财报数据
        logger.info("原始解析数据: %s", json.dumps(financial_data, indent=2, ensure_ascii=False))

        # ========== 5. 生成分析报告 ========== 
        logger.info("开始AI分析...")

        # 获取AI分析结果
        analysis = deepseek_client.analyze_financials(financial_data)
        logger.info("分析完成 | 结果长度: %d字符", len(analysis))
        logger.info("分析完成 | 结果内容: %s", analysis)

        # 结构化分析内容
        html_content = convert_markdown_to_html(analysis)

        import re
        result_text = re.sub(r'<think>.*?</think>', '', html_content, flags=re.DOTALL).replace("```markdown", "<br /><hr />")
        think_text = re.sub(r'```markdown.*?```', '', html_content, flags=re.DOTALL)
        # logger.info(json.dumps(think_text, indent=2, ensure_ascii=False))
        # logger.info(json.dumps(result_text, indent=2, ensure_ascii=False))
        logger.info(parse_input(analysis))

        # ========== 6. 响应结果 ========== 
        duration = (datetime.now() - start_time).total_seconds()
        logger.info("请求处理完成 | 耗时: %.2fs", duration)

        return jsonify(html=result_text)

    except ValueError as ve:
        logger.error("业务逻辑错误: %s", str(ve), exc_info=True)
        return jsonify(error=str(ve)), 400
    except requests.exceptions.RequestException as re:
        logger.error("API请求异常: %s", str(re), exc_info=True)
        return jsonify(error="后台服务暂不可用"), 503
    except Exception as e:
        logger.critical("未处理异常: %s", str(e), exc_info=True)
        return jsonify(error="系统内部错误"), 500
    finally:
        # 清理临时文件
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                logger.info("已清理临时文件: %s", filepath)
            except Exception as e:
                logger.warning("文件清理失败: %s", str(e))

def parse_input(text):
    """解析用户输入文本，提取结构化数据"""
    sections = re.split(r'\n\s*\n', text.strip())
    data = {'risks': [], 'growths': [], 'valuations': []}
    
    for section in sections:
        if '🚨' in section:
            # 提取风险数据
            risk_items = re.findall(r'(.+?)\n(.+?)(?=\n\n|\Z)', section, re.DOTALL)
            for title, desc in risk_items[:3]:
                value = re.search(r'[+-]?\d+\.?\d*%?', desc).group().replace('%','')
                data['risks'].append({
                    'name': title.strip(),
                    'value': float(value) if '%' not in value else float(value.replace('%',''))
                })
                
        elif '💡' in section:
            # 提取增长数据
            growth_items = re.findall(r'(.+?)\n(.+?)(?=\n\n|\Z)', section, re.DOTALL)
            for title, desc in growth_items[:3]:
                value = re.search(r'(\+?)(\d+\.?\d*)%', desc).group(2)
                data['growths'].append(float(value))
                
        elif '📈' in section:
            # 提取估值数据（示例逻辑，可根据实际需求调整）
            data['valuations'] = [85, 78, 65, 92]  # 示例数据，需根据文本分析
    
    return data

def convert_markdown_to_html(markdown_text):
    # 将 Markdown 转换为 HTML
    html_content = markdown.markdown(markdown_text)
    return html_content

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)

