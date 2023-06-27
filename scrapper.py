from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
import time
import pandas as pd
from termcolor import colored

driver = Chrome(executable_path='E:/A_InterviewPrep/Scrapper/chromedriver_win32/chromedriver.exe')
driver.get("https://builtin.com/companies")
driver.maximize_window()
driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

df = pd.DataFrame(columns=['CompanyURL', 'Position', 'PositionURL'])  # Replace column names as per your requirement
rows = []
count = 0
period = 1

def validTitle(title):
    escapeWords=["lead","staff","manager","director","principal","reliability","network","devops","process","security","wireless","control","chief","Clearance","senior","architect","Sr."]
    includeWords = ["software","full","web","react","front","back","data","python","javascript","associate","solution"]
    eject = True
    for word in escapeWords:
        if word.lower() in title.lower():
            print("Eject word: "+word.lower())
            eject=False
            break
    
    include=False
    for word in includeWords:
        if word.lower() in title.lower():
            print("Include word: "+word.lower())
            include=True
            break
    print(eject and include)
    return eject and include

def saveData():
    df = pd.DataFrame(rows)
    print(df.shape)
    excel_file_path = 'scrapped.xlsx'
    df.to_excel(excel_file_path, index=False)
    company = list(set(df['CompanyURL'].values.tolist()))
    df = pd.DataFrame({'CompanyNames':company})
    excel_file_path = 'companyNames.xlsx'
    df.to_excel(excel_file_path, index=False)

cardList = []
companyURL = []

s,p = 30,32

for i in range(s,p):
    driver.get("https://builtin.com/companies?page="+str(i))
    print("page "+str(i)+"/"+str(p-1))
    time.sleep(4+1)
    cardList = (driver.find_elements(By.CLASS_NAME,"company-card-col"))
    # print(cardList)
    for c in range(len(cardList)):
        domainList = cardList[c].find_elements(By.CLASS_NAME,"category-label")
        # print(domainList)
        if len(domainList)>0:
            # print(domainList[0].get_attribute("innerText"))
            if domainList[0].get_attribute("innerText")=="Developer + Engineer":
                url = (cardList[c].find_element(By.TAG_NAME,"a")).get_attribute('href')
                companyURL.append(url)



for i in range(len(companyURL)):
    print(i+1," of ",len(companyURL))
    url = companyURL[i]
    if len(rows)//period>count:
        count=len(rows)//period
        saveData()
    try:
        driver.get(url+"/jobs")
        # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(5+1)
        index = 4
        categoryButtons = driver.find_elements(By.CLASS_NAME,"category-col")
        if len(categoryButtons)==0:
            continue
        print('\n',url,'\n')
        # print("\n\n",url,len(categoryButtons),"\n\n")
        button = categoryButtons[index].find_element(By.TAG_NAME,"button")
        if not button.get_attribute("disabled")=="true":
            driver.execute_script("arguments[0].click();", button)
        time.sleep(5+1)

        positions = (driver.find_elements(By.CLASS_NAME,'job-row'))
        # if len(positions)==0:
        #     continue
        for p in positions:
            link = p.find_element(By.CLASS_NAME,"job-details-link").get_attribute("href")
            positionTitle = p.find_element(By.CLASS_NAME,"job-title").get_attribute("innerText")
            isValidTitle = validTitle(positionTitle)
            if isValidTitle:
                print(colored(positionTitle+"\t"+link,'green'))
                rows.append({"CompanyURL":url,"Position":positionTitle,"PositionURL":link})
            else:
                print(colored(positionTitle+"\t"+link,'red'))

        while True:
            nextButton = driver.find_elements(By.CLASS_NAME,"page-next")
            if len(nextButton) and (nextButton[0].is_enabled())==True:
                print((nextButton[0].get_attribute("disabled")))
                n = nextButton[0].find_element(By.TAG_NAME,'a')
                driver.execute_script("arguments[0].click();", n)
                # print(n.get_attribute('innerText'),(nextButton[0].is_enabled()))
                time.sleep(5+1)

                positions = (driver.find_elements(By.CLASS_NAME,'job-row'))
                for p in positions:
                    link = p.find_element(By.CLASS_NAME,"job-details-link").get_attribute("href")
                    positionTitle = p.find_element(By.CLASS_NAME,"job-title").get_attribute("innerText")
                    isValidTitle = validTitle(positionTitle)
                    if isValidTitle:
                        print(colored(positionTitle+"\t"+link,'green'))
                        rows.append({"CompanyURL":url,"Position":positionTitle,"PositionURL":link})
                    else:
                        print(colored(positionTitle+"\t"+link,'red'))

                        
                nextButton = driver.find_elements(By.CLASS_NAME,"page-next")
                n = nextButton[0].find_element(By.TAG_NAME,'a')
                print(n.get_attribute('tabindex'))
                if n.get_attribute('tabindex')=='-1':
                    print("break")
                    break
            else:
                break

    except Exception as e:
        print("An exception occurred for URL:", url)
        print("Exception:", str(e))
        continue
                  

saveData()
driver.quit()