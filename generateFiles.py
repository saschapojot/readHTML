import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
url="http://gernot-katzers-spice-pages.com/character_tables/"
response=requests.get(url)

response.encoding = 'utf-8'

content = response.text
GroupLinks=[]
if response.status_code==200:
    soup = BeautifulSoup(content, "html.parser")
    root = soup.find("html")
    body = root.find("body")
    p = body.find("p")
    table = p.find("table")
    AAll = table.find_all("a")
    hrefsAll=[elem["href"] for elem in AAll]
    for elem in hrefsAll:
        GroupLinks.append(elem)

groupNames=[re.sub("\.html","",link) for link in GroupLinks]

inCSVFile=pd.read_csv("32_list_point_group.csv",header=None)

namesInCSV=list(inCSVFile.iloc[:,0])
toBeParsed=[]
for i in range(0,len(groupNames)):
    if groupNames[i] not in namesInCSV:
        continue
    else:
        toBeParsed.append(GroupLinks[i])

print(len(toBeParsed))
print(len(namesInCSV))

print(sorted(toBeParsed))
print(sorted(namesInCSV))



