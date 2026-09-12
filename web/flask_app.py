# ChestSteward/web/flask_app.py
"""
flask_app 暂时不适用
"""
from flask import Flask, render_template_string

app = Flask(__name__)

# 简单的 Mermaid 预览页面
MERMAID_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mermaid Preview</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js">
    </script>
    <style>
        body { background: #1a1a1e; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        #container { background: #fff; padding: 30px; border-radius: 12px; max-width: 90%; }
        mermaid { background: white; }
    </style>
</head>
<body>
    <div id="container">
        <div id="mermaid-container">
            <pre class="mermaid">
                {{ code }}
            </pre>
        </div>
    </div>
    <script>
        mermaid.initialize({ startOnLoad: true, theme: 'base' });
    </script>
</body>
</html>
"""

@app.route('/mermaid')
def mermaid_preview():
    # 默认示例代码，后续通过 WebChannel 动态更新
    default_code = "graph TD\n    A[开始] --> B[结束]"
    return render_template_string(MERMAID_PAGE, code=default_code)

@app.route('/')
def index():
    return "<h1>ChestSteward Flask Service</h1><p>Mermaid 预览位于 <a href='/mermaid'>/mermaid</a></p>"