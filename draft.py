import requests
from bs4 import BeautifulSoup
import re


url="http://gernot-katzers-spice-pages.com/character_tables/"

response=requests.get(url)
# Optional: use chardet to detect encoding
# import chardet
#
# detected_encoding = chardet.detect(response.content)['encoding']
# response.encoding = detected_encoding
response.encoding = 'utf-8'

content = response.text

GroupLinks=[]
if response.status_code==200:
    # print("200")
    soup=BeautifulSoup(content,"html.parser")
    root=soup.find("html")
    body=root.find("body")
    p=body.find("p")
    table=p.find("table")
    AAll=table.find_all("a")
    a0=AAll[2]
    href0=a0["href"]
    GroupLinks.append(href0)

subPage=url+GroupLinks[0]
print(subPage)
tableStart=-1
tableEnd=-1

responseSubPage=requests.get(subPage)
if responseSubPage.status_code==200:
    responseSubPage.encoding="utf-8"
    contentStr=responseSubPage.text
    lines=contentStr.split("\n")
    for i in range(0,len(lines)):
        oneline=lines[i]
        if re.findall(r"Symmetry of Rotations and Cartesian products",oneline):
            tableStart=i
        if re.findall(r"Notes",oneline):
            tableEnd=i
# print(tableStart)
# print(tableEnd)
tableLines=[]
for i in range(tableStart,tableEnd+1):
    oneline=lines[i]
    if re.findall(r"SPAN",oneline):
        tableLines.append(oneline)

lineTmp=tableLines[0]
namePattern="<SPAN class=irred>(.*?)</SPAN> "
matchName=re.search(namePattern,lineTmp)

expressionPattern="<SPAN class=irred>.*?</SPAN>\s+(\d*[a-zA-Z]+(?:\+\d*[a-zA-Z]+)*)<SPAN class=obs>((?:\+\d*[a-zA-Z]+)*)</SPAN>"
matchExpression=re.search(expressionPattern,lineTmp)

expressionFormula=matchExpression.group(1)+matchExpression.group(2)

spanPattern="<SPAN.*?/SPAN>"
matchSpan=re.findall(spanPattern,lineTmp)


entries=matchSpan[2:]
subPattern=re.compile("<SUB>(?:<I>)?([a-zA-Z0-9]+)(?:</I>)?</SUB>")
supPattern=re.compile("<SUP>(?:<I>)?([a-zA-Z0-9]+)(?:</I>)?</SUP>")
leftBracePattern=re.compile("{")
rightBracePattern=re.compile("}")

spanClassPattern=re.compile('<SPAN[^>]*>')
spanRightPattern=re.compile("</SPAN>")
ILeftPattern=re.compile("<I>")
IRightPattern=re.compile("</I>")
def replace(oneSpanStr):
    """

    :param oneSpanStr: one entry in entries
    :return:
    """
    # print(oneSpanStr)
    matchLeftBrace = re.search(leftBracePattern, oneSpanStr)
    if matchLeftBrace:
        oneSpanStr = re.sub(leftBracePattern, "\{", oneSpanStr)

    matchRightBrace = re.search(rightBracePattern, oneSpanStr)
    if matchRightBrace:
        oneSpanStr = re.sub(rightBracePattern, "\}", oneSpanStr)
    # print(oneSpanStr)


    matchSub=re.search(subPattern,oneSpanStr)
    if matchSub:
        subVal=matchSub.group(1)
        print(subVal)
        oneSpanStr=re.sub(subPattern,"_{"+subVal+"}",oneSpanStr)
        # print(oneSpanStr)

    matchSup=re.search(supPattern,oneSpanStr)
    if matchSup:
        supVal=matchSup.group(1)
        oneSpanStr=re.sub(supPattern,"^{"+supVal+"}",oneSpanStr)
        # print(oneSpanStr)
    matchLeftI=re.findall(ILeftPattern,oneSpanStr)
    for matchTmp in matchLeftI:
        oneSpanStr=re.sub(matchTmp,"",oneSpanStr)

    matchRightI=re.findall(IRightPattern,oneSpanStr)
    for matchTmp in matchRightI:
        oneSpanStr=re.sub(matchTmp,"",oneSpanStr)
    spSpan=BeautifulSoup(oneSpanStr,"html.parser")
    for span in spSpan.find_all("span"):
        span.unwrap()
    stripped=str(spSpan)
    print(stripped)

    # matchSpClass=re.findall(spanClassPattern,oneSpanStr)
    #
    # for matchTmp in matchSpClass:
    #     print(matchTmp)
    #     print(oneSpanStr)
    #     oneSpanStr=re.sub(matchTmp,"",oneSpanStr)
    #     print(oneSpanStr)
    #
    #
    # matchRightSpan=re.findall(spanRightPattern,oneSpanStr)
    # for matchTmp in matchRightSpan:
    #     oneSpanStr=re.sub(matchTmp,"",oneSpanStr)

    # print(oneSpanStr)



print(entries[3])
replace(entries[3])