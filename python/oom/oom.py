import redis
import time
import sys
import logging

def setup_logging():
    """设置日志记录"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('memory_test.log', mode='w'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def test_redis_connection_under_memory_pressure():
    logger = setup_logging()
    try:
        r = redis.Redis(host='localhost', port=6379, password='enlink', socket_timeout=3, socket_connect_timeout=3, retry_on_timeout=False, health_check_interval=0, db=0)
        
        logger.info(f"test:{r.ping()}")
        
        memory_hog = []
        try:
            for i in range(1000):
                chunk = ' ' * 1024 * 1024 * 100
                memory_hog.append(chunk)
                
                try:
                    result = r.ping()
                    logger.info(f"{i}:Redis pass")
                except Exception as e:
                    logger.info(f"{i}:Redis fail-{e}")
                    break
                time.sleep(0.5)
                
        except MemoryError:
            logger.info("oom")
            
    except redis.ConnectionError as e:
        logger.info(f"init err: {e}")

if __name__ == "__main__":
    test_redis_connection_under_memory_pressure()