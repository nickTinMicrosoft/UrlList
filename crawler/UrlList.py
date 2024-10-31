import re
import urllib
from bs4 import BeautifulSoup
import pprint
import pandas as pd
import requests

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

urllist = []
urlDict = {}

class UrlList:
    def __init__(self, logger):
        self.logging = logger
        self.INDEX_NAME = os.getenv("INDEX_NAME", "crawler-index")
        self.BASE_URLS = os.getenv("BASE_URLS").split(',')


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

        print(f"local dict: {localDict}")   
        print(f"main dict: {urlDict}")
        self.logging.info(f"Done Scraping URL: {site}") 

       
        return localDict
    
 
    ## builds initial list to crawl through
    def InitDictionary(self, site):
        self.logging.info(f"Start building dictionary for crawling")
        
        localDict = self.ParseSite(site)
        print(f"from initDictionary: {localDict}")
        

        filterdDict = {url: description for url, description in localDict.items() if url and url.startswith("https://www.azcourts")}

        for url,description in filterdDict.items():
            # print(f"filtered url: {url}")
            
            if url not in urlDict:
                urlDict[url] = description
        
        self.logging.info(f"End building dictionary for crawling")

        
    def CrawlThroughList(self):
        ## this will iterate through each site in the dictionary
        # then get list of urls from each page, add to dictionary if not already in it
        # else ignore
        # 
        self.logging.info(f"Start crawling through dictionary")
        try:
            #iterate through dictionary
            for site in urlDict.keys():
                self.logging.info(f"Crawling on {site}")
                if site != self.BASE_URLS:
                    print(f"site from crawl: {site}")
                    # localDict = self.ParseSite(site)
        

        except requests.RequestException as e:
            self.logging.info(f"Error Crawling to site: {e}")

        self.logging.info(f"End crawling through dictionary")
        print(f"crawling")


    def startUrlList(self):
        self.logging.info("Initializing Build List and building Base List of URLS")
        for site in self.BASE_URLS:
            self.InitDictionary(site)
        
        self.CrawlThroughList()

        
        # for site in self.BASE_URLS:
        #     listbuilder(site)
        
        # print(f"list of urls: {urllist}")
        # print(f"urlDict: {urlDict}")

        ## next iterate through each url in list and continue to build the list \ dictionary 
        ## pop out any url that has already been scraped
        ## 
            




        


