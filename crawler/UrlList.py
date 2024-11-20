import re
import urllib
from bs4 import BeautifulSoup
import pprint
import pandas as pd
import requests
from azure.storage.blob import BlobServiceClient
import json

## imports from farhat
# from crawler.WebCrawler import WebCrawler
# from chunker.text_chunker import chunk_file_content
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
# from indexer.search_manager import create_search_index
# from indexer.search_manager import upload_documents_to_index
from azure.cosmos import CosmosClient, PartitionKey
from azure.identity import InteractiveBrowserCredential
from selenium.webdriver.common.by import By

import uuid, base64, os, time, requests, json
import queue, threading
import hashlib
from urllib.parse import urlparse

# from dotenv import load_dotenv
# load_dotenv()

linkList = []
urlDict = {}

class UrlList:
    def __init__(self, logger):
        self.logging = logger
        self.INDEX_NAME = os.getenv("INDEX_NAME", "crawler-index")
        self.BASE_URLS = os.getenv("BASE_URLS").split(',')
        self.NUM_OF_THREADS = os.getenv("NUM_OF_THREADS")
        self.EXCLUDE_LIST = os.getenv("EXCLUDE_LIST").split(',')
        self.DOMAIN = os.getenv("INCLUDE_DOMAINS")
        self.STORAGE_CONNECTION_STRING = os.getenv("STORAGE_CONNECTION_STRING")
        self.CONTAINER_NAME = os.getenv("CONTAINER_NAME")


        self.logging.info(f"Index Name: {self.INDEX_NAME}")
        self.logging.info(f"Base Urls: {self.BASE_URLS}")
        self.logging.info(f"Number of threads: {self.NUM_OF_THREADS}")
        self.logging.info(f"Exclude List: {self.EXCLUDE_LIST}")
        self.logging.info(f"Domain: {self.DOMAIN}")
        self.logging.info(f"Storage Container: {self.CONTAINER_NAME}")
        


    def ParseSite(self, site):
        self.logging.info(f"Scraping URL: {site}")
        localDict = {}

        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"}
        print(f"scraping site: {site}")
        
        webpage = requests.get(site, headers=headers)
        # print(f"content: {webpage.content}")
        
        soup = BeautifulSoup(webpage.content, 'html.parser')
        # print(f"soup: {soup}")

        for link in soup.find_all('a'):
            url = link.get('href')
            description = link.get_text(strip = True)

            localDict[url] = description

        # print(f"local dict: {localDict}")   
        # print(f"main dict: {urlDict}")
        self.logging.info(f"Done Scraping URL: {site}") 

       
        return localDict
    
 
    ## builds initial list to crawl through
    def InitDictionary(self, site):
        self.logging.info(f"Start building dictionary for crawling")
        
        localDict = self.ParseSite(site)
        # print(f"from initDictionary: {localDict}")
        

        ##INDEX ALL SITES ONLY CRAWL ON azcourts.gov
        ##WHITE LIST OF DOMAINES 

        filteredDict = {url: description for url, description in localDict.items() if url and url.startswith("https://www.azcourts.gov") and ".pdf" not in url}

        for url,description in filteredDict.items():
            # print(f"filtered url: {url}")
            
            if url not in urlDict:
                urlDict[url] = description
                linkList.append(url)

        self.logging.info(f"End building dictionary for crawling")

        
    def CrawlThroughList(self):
        ## this will iterate through each site in the dictionary
        # then get list of urls from each page, add to dictionary if not already in it
        # else ignore
        # 
        self.logging.info(f"Start crawling through list")
        try:
            #iterate through list
            for site in linkList:
                self.logging.info(f"Crawling on {site} in list")
                if site != self.BASE_URLS:
                    localDict = self.ParseSite(site)
                    filteredDict = {url: description for url, description in localDict.items() if url and url.startswith("https://") and ".pdf" not in url}
                    for url,description in filteredDict.items():
                    # print(f"filtered url: {url}")
            
                        if url not in urlDict:
                            print(f"adding {url} to dictionary")
                            self.logging.info(f"adding {url} to dictionary")
                            urlDict[url] = description

                            # if url not in linkList:
                            #     print(f"appending {url} to link list")
                            #     self.logging.info(f"appending {url} to link list")
                            #     linkList.append(url)

                        # else:
                        #     print(f"{url} already in dictionary")
                        #     self.logging.info(f"{url} already in dictionary")

                # linkList.pop(site)
     

        except requests.RequestException as e:
            self.logging.info(f"Error Crawling to site: {e}")

        self.logging.info(f"End crawling through dictionary")
        print(f"crawling")

    def writeFile(self):
        # Convert the dictionary to JSON
        json_data = json.dumps(urlDict)
        blob_name = "output.json"

        try:
            # Create a BlobServiceClient
            blob_service_client = BlobServiceClient.from_connection_string(self.STORAGE_CONNECTION_STRING)

            # Get a BlobClient for the specified container and blob
            blob_client = blob_service_client.get_blob_client(container=self.CONTAINER_NAME, blob=blob_name)

            # Upload the JSON data to the blob
            blob_client.upload_blob(json_data, overwrite=True)

            print(f"Successfully uploaded the dictionary to {blob_name} in the container {self.CONTAINER_NAME}.")
            self.logging.info(f"Successfully uploaded the dictionary to {blob_name} in the container {self.CONTAINER_NAME}.")
        except Exception as ex:
            print(f"An error occurred: {ex}")
            self.logging.info(f"An error occured writing file: {ex}")

        print(f"this will create the json file {blob_name}, in container {self.CONTAINER_NAME}")
        self.logging.info(f"this will create the json file {blob_name}, in container {self.CONTAINER_NAME}")

    def Index():
        print("this will pull the code and index")


    def startUrlList(self):
        self.logging.info("Initializing Build List and building Base List of URLS")

        for site in self.BASE_URLS:
            self.InitDictionary(site)
        

        ##write the dictionary to a file,, on the storage account
        ##indexer to get the file and load into the 

        self.CrawlThroughList()
        self.writeFile()


            




        


