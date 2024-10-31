import queue, threading
import uuid, base64, os, time, logging, requests
from datetime import datetime

from azure.cosmos import CosmosClient, PartitionKey
import hashlib

from dotenv import load_dotenv
from crawler.UrlList import UrlList

logging.basicConfig(filename=f'crawler-{time.time()}.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

load_dotenv()

if __name__ == "__main__":
    start_time = time.time()
    formatted_start_time = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")

    logging.info(f"Starting crawler: {formatted_start_time}")

    logger = logging.getLogger()

    urlList = UrlList(logger)
    urlList.startUrlList()

    end_time = time.time()
    formatted_end_time = datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M:%S")

    elapsed_time = end_time - start_time
    logging.info("Elapsed time: {:.2f} seconds".format(elapsed_time))
