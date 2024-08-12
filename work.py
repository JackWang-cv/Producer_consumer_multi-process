import threading
# from zhipu_ai_vision import send
from tencent_cos import upload_image_to_cos
import time
import logging
import os
from multi_process import ProducerConsumer, Photo

logger = logging.getLogger(__name__)

# 串行
# def detect(local_path):
#     start = time.time()
#     url = upload_image_to_cos(local_path)
#     logger.info(f'{url = }')
#     prompt = ""
#     reply = send(prompt, url)
#     logger.info(f'{reply = }')
#     end = time.time()
#     logger.info(f'use_times: {end-start}')

def list_images(directory, pc=None):
    prompts = ["You are a robot that checks if there is junk in the image. If there is junk in the image, please give only the English name of the junk,don't answer others; if not, please return None",
               'Check the pictures for a possible fire. If there is a risk of fire, return "fire"; If there is no risk of fire, return "None".',
               ['描述图片','以上描述若存在安全隐患则返回“异常行为”，反之返回“无”']]
    # 支持的图片扩展名
    image_extensions = ('.png', '.jpg', '.jpeg') 
    # 遍历目录下的所有文件
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(image_extensions):
                i = 1
                pc = ProducerConsumer()
                consumer_thread = threading.Thread(target=pc.consume)
                consumer_thread.start()
                url = upload_image_to_cos(os.path.join(root, file))
                for prompt in prompts:
                    pc.produce(Photo('session'+str(i), url, prompt))
                    i += 1
                time.sleep(1); # 模拟串行，在prompt并行
                pc.stop();
                consumer_thread.join();
                reply_message = pc.reply_message
                logger.info(f'{reply_message = }')
                # 可以添加处理reply_counts的代码
                
                # 串行
                # detect(os.path.join(root, file))

def head(file_content):
    total_start = time.time()
    list_images(file_content)
    total_end = time.time()
    logger.info(f'total_time: {total_end-total_start}')

    # pc = ProducerConsumer()
    # # 启动消费者线程
    # consumer_thread = threading.Thread(target=pc.consume)
    # consumer_thread.start()

    # total_start = time.time()
    # list_images(file_content)
    # list_images(file_content, pc)
    
    # time.sleep(1)
    # pc.stop()
    # consumer_thread.join()

    # total_end = time.time()
    # logger.info(f'total_time: {total_end-total_start}')