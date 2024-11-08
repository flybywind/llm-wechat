from llmagent.tkagent import main
from loguru import logger
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.exception(e)
