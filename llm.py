import requests
import json
import time


class LLM:
    def __init__(self, url, api_key, model, memory=False):
        self.url = url
        self.api_key = api_key
        self.model = model
        self.memory = memory
        self.history = []

        # 设置请求会话
        self.session = requests.Session()
        self.session.verify = False

    def add_message(self, role, content):
        """添加消息到历史记录"""
        self.history.append({"role": role, "content": content})

    def get_messages_literal(self):
        """获取消息列表的字面量表示"""
        return self.history.copy()

    def send(self, input_text, stream=False):
        """发送请求到API"""
        if not self.memory:
            self.history.clear()

        # 添加用户输入到历史
        self.add_message("user", input_text)

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        data = {
            "model": self.model,
            "messages": self.get_messages_literal(),
            "stream": stream
        }

        response = self.session.post(self.url, headers=headers, data=json.dumps(data))
        return response

    def parse_response(self, text, stream=False):
        """解析API响应"""
        try:
            json_data = json.loads(text)
            choices = json_data.get("choices", [])
            if not choices:
                return " "

            if stream:
                message = choices[0].get("delta", {})
            else:
                message = choices[0].get("message", {})

            content = message.get("content", " ")
            return content
        except (json.JSONDecodeError, KeyError, IndexError):
            return text if text else " "

    def chat(self, input_text):
        """非流式对话"""
        response = self.send(input_text, stream=False)
        if response.status_code == 200:
            output = self.parse_response(response.text, stream=False)
            # 添加助手回复到历史
            self.add_message("assistant", output)
            return output
        else:
            return f"Error: {response.status_code} - {response.text}"

    def chats(self, input_text, callback=None):
        """流式对话"""
        response = self.send(input_text, stream=True)
        output = []

        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        json_str = line_text[6:]  # 移除 'data: ' 前缀
                        if json_str.strip() == '[DONE]':
                            break

                        content = self.parse_response(json_str, stream=True)
                        if content:
                            output.append(content)
                            if callback:
                                callback(content)

            full_output = ''.join(output)
            # 添加助手回复到历史
            self.add_message("assistant", full_output)
            return full_output
        else:
            return f"Error: {response.status_code} - {response.text}"

    def preset(self, content, role="system"):
        """设置系统消息或预设对话"""
        self.add_message(role, content)
        self.memory = True

    def reset(self):
        """重置对话历史"""
        self.history.clear()


def initialize_model(url, api_key, model="DeepSeek-R1"):
    """初始化通用模型"""
    return LLM(url, api_key, model)


