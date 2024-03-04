import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import json

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

toBeParsedSorted=sorted(toBeParsed)
namesInCSVSorted=sorted(namesInCSV)

subPagesAll=[url+elem for elem in toBeParsedSorted]

outDict={}

for i in range(0,len(subPagesAll)):
    print("===========")
    pageToRead=subPagesAll[i]
    grpName=namesInCSVSorted[i]
    print("group "+grpName)
    # print(pageToRead)
    # print(grpName)
    tableStart = -1
    tableEnd = -1
    responseSubPage = requests.get(pageToRead)
    if responseSubPage.status_code!=200:
        print("page "+pageToRead+" cannot be read")
        continue
    else:
        dictForThisPage={}
        responseSubPage.encoding = "utf-8"
        contentStr = responseSubPage.text
        lines = contentStr.split("\n")
        for i in range(0, len(lines)):
            oneline = lines[i]
            if re.findall(r"Symmetry of Rotations and Cartesian products", oneline):
                tableStart = i
            if re.findall(r"Notes", oneline):
                tableEnd = i
        tableLines = []
        for i in range(tableStart, tableEnd + 1):
            oneline = lines[i]
            if re.findall(r"SPAN", oneline):
                tableLines.append(oneline)
        namePattern =re.compile("<SPAN class=irred>(.*?)</SPAN> ")
        expressionPattern =re.compile("<SPAN class=irred>.*?</SPAN>\s+(\d*[a-zA-Z]+(?:\+\d*[a-zA-Z]+)*)?<SPAN class=obs>((?:\+?\d*[a-zA-Z]+)+)</SPAN>")
        spanPattern = re.compile("<SPAN.*?/SPAN>")
        spanOverPattern = re.compile("(<SPAN class=over>)(.*?)(</SPAN>)")
        for lineTmp in tableLines:
            lineList=[]
            matchName=re.search(namePattern,lineTmp)
            print("name="+matchName.group(1))
            # print(matchName.group(1))
            matchExpression = re.search(expressionPattern, lineTmp)
            if matchExpression!=None:
                # print(matchExpression)
                # print("expression1="+matchExpression.group(1))
                if matchExpression.group(1)==None:
                    expressionFormula=matchExpression.group(2)
                else:
                    expressionFormula= matchExpression.group(1) + matchExpression.group(2)
                # print("expression2="+matchExpression.group(2))
                # expressionFormula = matchExpression.group(1) + matchExpression.group(2)
                print(expressionFormula)
            lineList.append(expressionFormula)
            #remove <SPAN class=over>.*?</Span>
            matchOver=re.findall(spanOverPattern,lineTmp)
            def replacement(match):
                return f"{match.group(2)}"
            lineTmp=re.sub(spanOverPattern,replacement,lineTmp)



            #replace \u2212 with literal "-"
            lineTmp=lineTmp.replace("\u2212","-")
            matchSpan = re.findall(spanPattern, lineTmp)
            entries = matchSpan[2:]
            subPattern = re.compile("<SUB>(?:<I>)?([a-zA-Z0-9]+)(?:</I>)?</SUB>")
            supPattern = re.compile("<SUP>(?:<I>)?([a-zA-Z0-9]+)(?:</I>)?</SUP>")
            leftBracePattern = re.compile("{")
            rightBracePattern = re.compile("}")
            spanClassPattern = re.compile('<SPAN[^>]*>')
            spanRightPattern = re.compile("</SPAN>")
            ILeftPattern = re.compile("<I>")
            IRightPattern = re.compile("</I>")
            sqrtPattern=re.compile("(&radic;)")


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

                matchSub = re.search(subPattern, oneSpanStr)
                if matchSub:
                    subVal = matchSub.group(1)
                    # print(subVal)
                    oneSpanStr = re.sub(subPattern, "_{" + subVal + "}", oneSpanStr)
                    # print(oneSpanStr)

                matchSup = re.search(supPattern, oneSpanStr)
                if matchSup:
                    supVal = matchSup.group(1)
                    oneSpanStr = re.sub(supPattern, "^{" + supVal + "}", oneSpanStr)
                    # print(oneSpanStr)

                matchSqrt=re.search(sqrtPattern,oneSpanStr)
                if matchSqrt:
                    # print("-----------------")
                    # print("before replace sqrt: ", oneSpanStr)
                    mt1=matchSqrt.group(1)
                    # print("mt1="+mt1)

                    # mt2=matchSqrt.group(2)
                    # print("mt2=" + mt2)
                    oneSpanStr=re.sub(mt1,"\\\sqrt{",oneSpanStr)
                    # oneSpanStr=re.sub(mt2,mt2+"}",oneSpanStr)
                    # print("after replacing sqrt: ",oneSpanStr)
                    # print("------------")
                    # print(mt1)
                    # print(mt2)

                matchLeftI = re.findall(ILeftPattern, oneSpanStr)
                for matchTmp in matchLeftI:
                    oneSpanStr = re.sub(matchTmp, "", oneSpanStr)

                matchRightI = re.findall(IRightPattern, oneSpanStr)

                for matchTmp in matchRightI:
                    oneSpanStr = re.sub(matchTmp, "", oneSpanStr)
                # print("after removing I: " + oneSpanStr)
                spSpan = BeautifulSoup(oneSpanStr, "html.parser")
                for span in spSpan.find_all("span"):
                    span.unwrap()
                stripped = str(spSpan)
                # print("after removing span: " + stripped)
                return stripped
            for i in range(0,len(entries)):
                # print("***")
                #
                # print("entry i="+entries[i])
                lineList.append(replace(entries[i]))


            dictForThisPage[matchName.group(1)]=lineList
    outDict[grpName]=dictForThisPage


with open("grp.json","w+") as fptr:
    json.dump(outDict,fptr)




















