import requests
import json
import warnings
from urllib3.exceptions import InsecureRequestWarning

from llm import initialize_model

# 抑制SSL警告
warnings.filterwarnings("ignore", category=InsecureRequestWarning)


def load_system_prompt(file_path="system_prompt.txt"):
    """从文件加载系统提示词"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()


if __name__ == '__main__':
    # 初始化模型
    url = "https://maas-cn-southwest-2.modelarts-maas.com/v1/infers/8a062fd4-7367-4ab4-a936-5eeb8fb821c4/v1/chat/completions"
    api_key = "ZmWjmmzU_4z4zZCMdrhOdthpeUiHSbZN7bQ_-_tIMyRZh0ciAEe89roysh1CpUK89EVs6nJmauAzICSPIyPz5w"

    model = initialize_model(url, api_key)

    # 设置系统提示
    system_prompt = load_system_prompt()

    model.preset(system_prompt, "system")

    # 持续对话示例
    while True:
        user_input = input("\n用户: ").strip()
        if user_input.lower() in ['退出', 'quit', 'exit']:
            break

        print("助手: ", end="", flush=True)

        # 使用流式输出
        def print_chunk(chunk):
            print(chunk, end="", flush=True)


        response = model.chats(user_input, callback=print_chunk)
        print()  # 换行

        # 或者使用非流式输出
        # response = model.chat(user_input)
        # print(f"助手: {response}")
