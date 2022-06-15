#encoding=utf-8
import json
import urllib.parse as urlps
import glob
import os
import re

onlyNum=re.compile(r'[0-9\.]*$')

# target item's position
targetCompPos={
    "allMoney":[29,35.0,16.5,19.0],
    "itemName":[0,10,9,16],
    "itemNum":[0,0,0,0]
}


# read the pdf's page generated from 
def readText(jsonFilePath):
    with open(jsonFilePath,'r',encoding='utf-8') as f:
        b=json.load(f)
    return b['Pages']


# 带空格的数量
numHead='%E6%95%B0%20'
numHead2='%E6%95%B0%E3%80%80%E9%87%8F'
# 单价
singlePrice='%E5%8D%95%20'
singlePrice2='%E5%8D%95%E3%80%80%E4%BB%B7'
# update the number's information
def updateItemNumPos(testList):
    for curText in testList:
        textnow=curText['R'][0]['T']
        if numHead in textnow or numHead2 in textnow:
            curleft=curText['x']
        elif singlePrice in textnow or singlePrice2 in textnow:
            curright=curText['x']
    
    targetCompPos["itemNum"]=[curleft,curright,targetCompPos["itemName"][2],targetCompPos["itemName"][3]]
    print(targetCompPos["itemNum"])


# sorted the numList with y position
def generateNumList(matchRes):
    itemNumList=[[x['y'],x['R'][0]['T']] for x in matchRes]
    itemNumList=sorted(itemNumList, key=lambda x:x[0])
    # print(itemNumList)
    return itemNumList


# 合计中间有空格
tototal='%E5%90%88%20%20'
# 合计中间没有空格，直接判断一个单独的合字
tototal2='%E5%90%88'
# 小计
littletotal='%E5%B0%8F%E8%AE%A1'
# 货物
itemHead='%E8%B4%A7%E7%89%A9%E6%88%96%E5%BA%94%E7%A8%8E%E5%8A%B3%E5%8A%A1%E3%80%81'
itemHead2='%E8%B4%A7%E7%89%A9(%E5%8A'
itemHead3='%E8%B4%A7%E7%89%A9%EF%BC%88%E5%8A%B3%E5%8A%A1%EF%BC%89%E5%90%8D%E7%A7%B0'
# 规格型号
modelText='%E8%A7%84%E6%A0%BC%E5%9E%8B%E5%8F%B7'
# update the item's position
def updateItemPos(testList):
    for curText in testList:
        textnow=curText['R'][0]['T']
        if textnow.startswith(tototal) or textnow==tototal2 or littletotal in textnow:
            curbottom=curText['y']
        elif itemHead in textnow or itemHead2 in textnow or itemHead3 in textnow:
            curtop=curText['y']
        elif modelText in textnow:
            curright=curText['x']-2
    targetCompPos['itemName'][1],targetCompPos['itemName'][2],targetCompPos['itemName'][3]=curright,curtop,curbottom


# mapping the item info to the number
def generateItemList(matchRes,itemNumList):
    itemList=generateNumList(matchRes)
    itemAllNameList=[]
    curItemIndex=1
    curItemName=''

    if len(itemNumList)>1:
        nextItemY=itemNumList[1][0]
    else:
        nextItemY=1000
    
    for itemInfo in itemList:
        if itemInfo[0]<nextItemY:
            curItemName+=itemInfo[1]
        else:
            itemAllNameList.append(curItemName)
            curItemName=''

            curItemIndex+=1
            if len(itemNumList)>curItemIndex:
                nextItemY=itemNumList[curItemIndex][0]
            else:
                nextItemY=1000
            
            curItemName+=itemInfo[1]
    itemAllNameList.append(curItemName)

    # print(itemNumList)
    # print(itemList)
    # print(itemAllNameList)
    return itemAllNameList


# search all the text data that matched the position
def matchComp(targetNum,testList):
    resAll=[]
    for curText in testList:
        x=curText['x']
        y=curText['y']
        if x>targetNum[0] and x<targetNum[1] and y>targetNum[2] and y<targetNum[3]:
            # print(urlps.unquote(curText['R'][0]['T']))
            # print(onlyNum.findall(urlps.unquote(curText['R'][0]['T'])))
            # resAll+= onlyNum.findall(urlps.unquote(curText['R'][0]['T']))[0]
            resAll.append(curText)
    return resAll


# concatenate the total price text
def moneyGen(matchRes):
    curText=''
    for eachRes in matchRes:
        curText+=eachRes['R'][0]['T']
    return onlyNum.findall(urlps.unquote(curText))[0]


# match all the target component
def scanAllComp(testList):
    # update the relative position
    updateItemPos(testList)
    updateItemNumPos(testList)

    itemInfo=[]
    numList=[]
    allMoney=0
    for curComp in targetCompPos.keys():
        seaRet=matchComp(targetCompPos[curComp],testList)

        if seaRet:
            if curComp=='allMoney':
                allMoney=moneyGen(seaRet)
                print(curComp+': '+allMoney)
            elif curComp=='itemNum':
                numList=generateNumList(seaRet)
                # print(curComp+': '+urlps.unquote(seaRet))
            elif curComp=='itemName':
                itemInfo=seaRet
        
    itemList=generateItemList(itemInfo,numList)
    return allMoney,numList,itemList


# output the result, could be customed to output all the info you need
def outputInfo(ticketPath,allMoney,numList,itemList):
    # print("all Money: "+allMoney)
    # print("numList: ")
    # print(numList)
    # print("itemList: ")
    # print(itemList)

    if len(numList)!=len(itemList): # sometimes meet this situation, just manaully check it
        # print(urlps.unquote(itemList[0]))
        print(len(numList))
        print(len(itemList))
        for i in itemList:
            print(urlps.unquote(i))
            print('------')
        print("item less than num")

    with open('tmpoutput.txt','a',encoding='utf-8') as f:
        f.write(os.path.basename(ticketPath).replace('.json','.pdf')+'\n')
        for i in range(0,len(numList)):
            f.write(urlps.unquote(itemList[i])+"\t"+numList[i][1])
            if i==0:
                f.write('\t'+allMoney+'\n')
            else:
                f.write('\n')
        for i in range(len(numList),len(itemList)):
            f.write(urlps.unquote(itemList[i])+'\n')
        f.write('\n')


# scan all the json file in one directory, and support multi pages tickets
def scanResult(resDirPath):
    for curTicketPath in glob.iglob(os.path.join(resDirPath,'*.json')):
        allText=readText(curTicketPath)
        print(curTicketPath)
        if len(allText)>1:
            allMoney,_,_=scanAllComp(allText[0]['Texts'])
            numList=[]
            itemList=[]
            for resPage in range(1,len(allText)):
                _,curNumList,curItemList=scanAllComp(allText[resPage]['Texts'])
                numList.extend(curNumList)
                itemList.extend(curItemList)
        else:
            allText=allText[0]['Texts']
            allMoney,numList,itemList=scanAllComp(allText)
            # print(allMoney,numList,itemList)

        # print(allMoney,numList,itemList)
        outputInfo(curTicketPath,allMoney,numList,itemList)
        

if __name__=='__main__':
    scanResult('result')
