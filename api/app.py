import time
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 全局变量(注:Serverless 环境下全局变量可能在实例“温存”期间有效,但不保证长久保存)
current_node_url = "https://www.xxxx.net/api/v1/client/subscribe?token=cd68e279713175a66ae7284bbxxx"
current_node_config = None
last_update_time = 0
update_interval = 3600  # 更新间隔(秒),此处设置为 1 小时

def update_node_config(force_update=False):
    """根据当前节点 URL 更新配置(若超时或强制更新)"""
    global current_node_config, last_update_time
    now = time.time()
    if force_update or (now - last_update_time > update_interval):
        try:
            response = requests.get(current_node_url)
            if response.status_code == 200:
                current_node_config = response.text
                last_update_time = now
                print("节点配置已更新")
            else:
                print("获取节点配置失败, 状态码:", response.status_code)
        except Exception as e:
            print("更新节点配置时发生错误:", e)

@app.route('/')
def index():
    """显示输入更新 URL 的页面"""
    return render_template('index.html', current_url=current_node_url)

@app.route('/update-url', methods=['POST'])
def update_url():
    """通过表单更新节点 URL,并强制更新一次节点配置"""
    global current_node_url
    new_url = request.form.get('node_url')
    if new_url:
        current_node_url = new_url
        update_node_config(force_update=True)
        message = "节点 URL 更新成功!"
        return render_template('index.html', current_url=current_node_url, message=message)
    else:
        message = "请输入有效的 URL"
        return render_template('index.html', current_url=current_node_url, message=message)

@app.route('/get-node-config', methods=['GET'])
def get_node_config():
    """返回当前最新的节点配置(如果超过更新间隔则先更新)"""
    update_node_config()  # 懒更新
    if current_node_config:
        return current_node_config
    else:
        return jsonify({"error": "节点配置尚未加载"}), 500

# 仅用于本地调试运行,在 Vercel 部署时入口为 app 对象
if __name__ == '__main__':
    app.run(debug=True)
