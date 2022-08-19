# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 12:56:50 2022

@author: kanno
"""

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
from urllib.parse import parse_qs
import os, time, json

# Set client directory for working files
client_dir = r"C:\Users\kanno\Desktop\WCU"
os.chdir(client_dir)

if __name__ == "__main__":
    # Enable Performance Logging in Chrome
    desired_capabilities = DesiredCapabilities.CHROME
    desired_capabilities["goog:loggingPrefs"] = {"performance" : "ALL"}
    
    # Create the webdriver object and pass the arguements
    options = webdriver.ChromeOptions()
    
    # Chrome starts in Headless mode
    options.add_argument('headless')
    
    # Ignore cert errors
    options.add_argument("--ignore-certificate-errors")
    
    # Startup Chrome webdriver w/ exe path and pass options as params
    driver = webdriver.Chrome(ChromeDriverManager().install(),
                              options=options,
                              desired_capabilities=desired_capabilities)
    
    # Send a request to the website and pause
    driver.get("https://westcoastuniversity.edu/")
    time.sleep(10)
    
    # Capture logs from Chrome Performance DevTools
    logs = driver.get_log("performance")
    
    # Opens a writeable JSON file and writes the logs into file
    with open("network_log.json", "w", encoding = "utf-8") as f:
        f.write("[")
        
        # Iterate over all logs and parse with JSON
        for log in logs:
            network_log = json.loads(log["message"])["message"]
            
            # Checks if the current 'method' key has a network value
            if("Network.response" in network_log["method"]
               or "Network.request" in network_log["method"]
               or "Network.webSocket" in network_log["method"]):

                # Writes network log to JSON file
                f.write(json.dumps(network_log) + ",")
        f.write("{}]")
        
    print("Quitting Selenium WebDriver")
    driver.quit()
    
    # Read the JSON file and parse for GA and GTM IDs
    json_file = "network_log.json"
    with open(json_file, "r", encoding = "utf-8") as f:
        logs = json.loads(f.read())
        gtm_lst = []
        ua_lst = []
        ga4_lst = []
        
        for log in logs:
            try: 
                url = log["params"]["request"]["url"]
                if url.find("tid=") != -1:
                    ga_id = parse_qs(urlparse(url).query)['tid'][0]
                    if parse_qs(urlparse(url).query)['v'][0] == "1":
                        ua_lst.append(ga_id)
                    if parse_qs(urlparse(url).query)['v'][0] == "2":
                        ga4_lst.append(ga_id)
                if url.find("gtm.js") != -1:
                    ga_id = parse_qs(urlparse(url).query)['id'][0]
                    gtm_lst.append(ga_id)
            except Exception:
                pass
        
        gtm_lst = [*set(gtm_lst)]
        ua_lst = [*set(gtm_lst)]
        ga4_lst = [*set(ga4_lst)]