import threading
# from zhipu_ai_vision import send
# from tencent_cos import upload_image_to_cos
import time
import logging
import os
from multi_process import ProducerConsumer, Photo

logger = logging.getLogger(__name__)

# 串行
# def detect(local_path):
#     start = time()
#     url = upload_image_to_cos(local_path)
#     prompt = "你是一个检查图片中是否有垃圾的机器人。如果图片中有垃圾，请返回垃圾的类别；如果没有，请返回无。"
#     reply = send(prompt, url)
#     logger.info(f'{reply = }')
#     end = time()
#     logger.info(f'use_times: {end-start}')

def list_images(directory, pc):
    # 支持的图片扩展名
    image_extensions = ('.png', '.jpg', '.jpeg') 
    # 遍历目录下的所有文件
    i = 1
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(image_extensions):
                # 并行
                pc.produce(Photo('session'+str(i), os.path.join(root, file)))
                i += 1
                # 串行
                # detect(os.path.join(root, file))

def head(file_content):
    pc = ProducerConsumer()
    # 启动消费者线程
    consumer_thread = threading.Thread(target=pc.consume)
    consumer_thread.start()

    total_start = time.time()
    list_images(file_content, pc)
    
    time.sleep(1)
    pc.stop()
    consumer_thread.join()

    reply_counts = pc.get_reply_counts()
    logger.info(f'{reply_counts = }')
    total_end = time.time()
    logger.info(f'total_time: {total_end-total_start}')
    
    
    