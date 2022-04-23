import time
import pandas as pd
from selenium import webdriver
from web3 import Web3
import shared
shared.init()

df_healthy_tokens = []
driver = webdriver.Firefox(executable_path="./geckodriver")  # You need to download geckodriver

for j in range(1, 7):
    for i in range(1, 51):
            driver.get(f"https://polygonscan.com/tokens?p={j}")
            time.sleep(3)
            try:
                token_name = driver.find_element_by_xpath(f'/html/body/div[1]/main/div[2]/div/div[2]/div/div/div[2]'
                                                          f'/div[2]/table/tbody/tr[{i}]/td[2]/div/div/h3/a').text
            except:
                driver.execute_script(f"window.scrollTo(0, 1080)")
                time.sleep(2)

            driver.find_element_by_xpath(f'/html/body/div[1]/main/div[2]/div/div[2]/div/div/div[2]/div[2]/table/'
                                         f'tbody/tr[{i}]/td[2]/div/div/h3/a').click()
            time.sleep(3)
            token_address = driver.find_element_by_xpath('/html/body/div[1]/main/div[4]/div[1]/div[2]/div/div[2]'
                                                         '/div[1]/div[2]/div').text
            token_address = Web3.toChecksumAddress(token_address)
            df_healthy_tokens.append([token_name, token_address])
            print(token_name, token_address)

    pd.DataFrame(df_healthy_tokens).to_csv("healthy_tokenss.csv", index=False)

