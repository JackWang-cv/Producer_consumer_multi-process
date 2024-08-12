# pip install zhipuai 请先在终端进行安装

from zhipuai import ZhipuAI

def glm4(text):
    client = ZhipuAI(api_key="")

    response = client.chat.completions.create(
        model="glm-4",
        messages=[
            {
                "role": "system",
                "content": "你是智能安全防范机器人，输入中的描述若存在安全隐患则返回“异常行为”，反之返回“无”,不用返回其他的" 
            },
            {
                "role": "user",
                "content": text
            }
        ],
        top_p= 0.7,
        temperature= 0.95,
        max_tokens=10,
        tools = [{"type":"web_search","web_search":{"search_result":True}}],
        stream=False
    )
    return response.choices[0].message