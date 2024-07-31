import threading
import time
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Counter
from zhipu_ai_vision import send
from tencent_cos import upload_image_to_cos
import logging
logger = logging.getLogger(__name__)

class Photo:
    def __init__(self, session_id, url):
        self.session_id = session_id
        self.url = url

# ThreadPoolExecutor：控制应用级别的全局线程数，管理所有任务的并发。
# BoundedSemaphore：控制特定会话中线程的并发访问，防止会话中的过多并发线程。

class ProducerConsumer:
    def __init__(self):
        self.sessions = {}
        self.lock = threading.Lock()
        self.handler_pool = ThreadPoolExecutor(max_workers=20)
        self.futures = {}
        self.running = True  # 控制循环的标志变量
        self.reply_counter = Counter()  # 线程安全的计数器
        self.reply_counter_lock = threading.Lock()  # 锁保护计数器

    def conf(self):
        return {"concurrency_in_session": 4}

    def produce(self, photo):
        session_id = photo.session_id
        with self.lock:
            if session_id not in self.sessions:
                # 创建一个信号量
                self.sessions[session_id] = [photo, threading.BoundedSemaphore(self.conf().get("concurrency_in_session", 4))]
            else:
                # 更新已有 session_id
                self.sessions[session_id][0] = photo

    def _thread_pool_callback(self, session_id, photo):
        def callback(future):
            try:
                result = future.result()
                print(f"Task completed for session: {session_id}, photo: {photo.url}")
            except Exception as e:
                print(f"Error processing task for session: {session_id}, photo: {photo.url}, error: {e}")
            finally:
                with self.lock:
                    self.sessions[session_id][1].release()
        return callback

    def _handle(self, photo):
        try:
            # 处理逻辑
            url = upload_image_to_cos(photo.url)
            prompt = "You are a robot that checks if there is junk in the image. If there is junk in the image, please give only the English name of the junk,don't answer others; if not, please return None."
            reply = send(prompt, url)
            with self.reply_counter_lock:
                self.reply_counter[reply.content] += 1
            logger.info(f'{reply.content = }, {photo.url = }')

        except Exception as e:
            print(f"Error handling photo: {photo.url}, error: {e}")

    def consume(self):
        while self.running or any(semaphore._value < semaphore._initial_value for _, semaphore in self.sessions.values()):
            with self.lock:
                session_ids = list(self.sessions.keys())
                for session_id in session_ids:
                    _, semaphore = self.sessions[session_id]
                    if semaphore.acquire(blocking=False):  # 尝试获取信号量
                        # 获取 URL
                        photo = self.sessions[session_id][0]
                        if photo:  # 处理 URL
                            # print(f"Consume URL: {photo}")
                            future: Future = self.handler_pool.submit(self._handle, photo)
                            future.add_done_callback(self._thread_pool_callback(session_id, photo=photo))
                            self.sessions[session_id][0] = None
                            if session_id not in self.futures:
                                self.futures[session_id] = []
                            self.futures[session_id].append(future)
                        elif semaphore._initial_value == semaphore._value + 1:  # 所有任务都处理完毕
                            if session_id in self.futures:
                                self.futures[session_id] = [t for t in self.futures[session_id] if not t.done()]
                                assert len(self.futures[session_id]) == 0, "thread pool error"
                            del self.sessions[session_id]
                        else:
                            semaphore.release()
                        # logger.info(f'{semaphore._value = }')
            time.sleep(0.1)

    def stop(self):
        self.running = False
        self.handler_pool.shutdown(wait=True)

    def get_reply_counts(self):
        with self.reply_counter_lock:
            return dict(self.reply_counter)

if __name__ == "__main__":
    pass
    # pc = ProducerConsumer()

    # # 启动消费者线程
    # consumer_thread = threading.Thread(target=pc.consume)
    # consumer_thread.start()

    # # 生成一些消息
    # for i in range(5):
    #     pc.produce(Photo(session_id="session"+str(i), url=f"Message {i}"))
