from zhipuai import ZhipuAI
# 词条改一下，变成
def send(text, url):
    client = ZhipuAI(api_key="")
    response = client.chat.completions.create(
        model="glm-4v",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": url
                        }
                    }
                ]
            }
        ],
        top_p=0.7,
        temperature=0.2,
        max_tokens=1024,
        stream=False,
    )
    return response.choices[0].message


if __name__ == "__main__":

    # print(send("检查图片是否有可能发生火灾。如果存在火灾的风险，请返回“有”；如果没有火灾风险，请返回“无”。","https://zhipuai-on-wechat-1319111495.cos.ap-guangzhou.myqcloud.com/19.png").content)
    pass
    