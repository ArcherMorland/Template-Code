# -*- coding: utf8 -*-

from selenium import webdriver
import requests
from lxml import etree, html #sudo pip3.5 install lxml
from bs4 import BeautifulSoup #pip3.5 install beautifulsoup4
#import xlrd
import socks # $> pip3 install PySocks

from html.parser import HTMLParser
from time import sleep
from datetime import date
import urllib
import urllib.request
import os, platform, sys, getpass, codecs, time, datetime, copy
from random import randint
import socket


def initialize():
    preservation_interval=3#days
    SequenceMark_int=0
    Last_SeqMark_int=1
    if(True):
        SequenceMark_int=randint(1,10**12-1)
        SequenceMark="{:0>{prec}d}".format(SequenceMark_int,prec=12)
        Last_SeqMark_int=randint(1,10**12-1)
    return 0

class ApoSysConf:
    def __init__(self):

        opsys=platform.system()
        
        if opsys=='Windows':
            self.path_cff=r"configuration\Path.conf"
            
        elif opsys=='Linux':
            self.path_cff="configuration/Path.conf"

        else:
            self.path_cff=None
        

        
    def OSinfo(self):
        infoDict={
            
            "system":platform.system(),   # 'Windows'
            "release":platform.release(),   #  '10'
            "version":platform.version(),   #  '10.0.14393'
            "machine":platform.machine(),   #   'AMD64'
            "processor":platform.processor(),   #  'Intel64 Family 6 Model 78 Stepping 3, GenuineIntel'
            "nodeName":platform.node(),   #  'ASCLEPIUS'
            #"User":getpass.getuser(),     #'Archer'
                        
            }

        return infoDict


    
    def PathConf(self):
        
        path=self.path_cff        
        f=open(path,'r')
        lines=f.readlines()        
        f.close()

        asc=ApoSysConf()
        osi=asc.OSinfo()
        pathDict=dict(
                      WebDriverPath="",
                      Default_DownloadPath="",
                      LogPath=""
                      )
        if(osi["system"]=="Linux"):
            pathDict.update({"WebDriverPath" : os.path.join("BrowserDrivers","Chrome","chromedriver")    })
            pathDict.update({"Default_DownloadPath":"Downloads"})
            pathDict.update({"LogPath" : os.path.join("configuration","Event.log")    })


        elif(osi["system"]=="Windows"):
            pathDict.update({"WebDriverPath": r"BrowserDrivers\Chrome\chromedriver.exe"})#r"BrowserDrivers\Chrome\chromedriver.exe"
            pathDict.update({"Default_DownloadPath":"Downloads"})
            pathDict.update({"LogPath":r"configuration\Event.log"})
                           
        return pathDict    

    def DBconf():
        result=dict()
        f=open(os.path.abspath(os.path.join("configuration","DBConn","Settings")),"r")
        lines=f.readlines()
        f.close()
        
        l=0
        for line in lines:
            line=line.replace("\n","")
            if (l>0):
                ll=line.split(',')
                ll_connstr=copy.deepcopy(ll)#ll[:]#
                ll_connstr.remove(ll[0])
                result.update({ll[0]:ll_connstr})
            l+=1
        return result   


def CleanTempFiles():
    try:
        location_AppTemp=r"C:\Users\vamdo\AppData\Local\Temp"
        return True
    except:
        return False
        
    



class apophis:
    
    def __init__(self, TargetWebsite, WebDriverPath = None):
        asc=ApoSysConf()
        PathDict=asc.PathConf()

        self.TargetWebsite = TargetWebsite   #"http://goodinfo.tw/StockInfo/ShowK_Chart.asp?STOCK_ID=1303&CHT_CAT2=DATE"

        self.Default_DownloadPath= PathDict["Default_DownloadPath"]# "Downloads"
        
        if (WebDriverPath != None ):
            self.WebDriverPath = WebDriverPath   
        else:
            self.WebDriverPath = PathDict["WebDriverPath"]
           

        self.LogPath= PathDict["LogPath"]
        
    def RegularDownloadFiles(self, ButtonName="", DownloadPath=None, TargetWebsite= None, WebDriverPath=None):

        if (TargetWebsite is None):
            TargetWebsite=self.TargetWebsite
            
        if (DownloadPath is None):
            DownloadPath=self.Default_DownloadPath
            
        if (WebDriverPath is None):
            WebDriverPath=self.WebDriverPath


        while (not os.path.exists( DownloadPath )  ):
            print("The path :\"{path}\" doesn't exists.\n".format(path = DownloadPath))
            
            decision=input("Do you want to use another path for file downloaded?  Y/N  : ")

            if (decision == 'Y' or decision == 'y'):
                DownloadPath=input("Input a new path for download.  :  \n")
            else:
                return 0
            
            
        print("The path :\"{path}\" .\n".format(path = DownloadPath))
        
        options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': os.path.abspath(DownloadPath) }#修改下載目的資料夾:Python selenium —— 文件下載，不彈出窗口，直接下載到指定路徑
        options.add_experimental_option('prefs', prefs)
        options.add_argument('--proxy-server=http://127.0.0.1:8118')
        

        browser = webdriver.Chrome(executable_path= WebDriverPath , chrome_options=options)
        

        try:
            browser.get( TargetWebsite )#url
            NEXT_BUTTON_XPATH1 = '//input[@type="button" and @value="'+ButtonName+'"]'#
            browser.find_element_by_xpath(NEXT_BUTTON_XPATH1).click()
            
            sleep(8)

            browser.get("http://icanhazip.com/")
            htmlContext=browser.page_source
            htmlContext_str=str(htmlContext)
            sp=BeautifulSoup(htmlContext_str,"html.parser")

            rows=sp.find_all("pre")
            for row in rows:
                value=row.string
                ip=str(value)

            CurrentIP=ip

            print("current IP : {IP} ".format(IP=CurrentIP))
            

        except:
            browser.get("http://icanhazip.com/")
            htmlContext=browser.page_source
            htmlContext_str=str(htmlContext)
            sp=BeautifulSoup(htmlContext_str,"html.parser")
            rows=sp.find_all("pre")
            for row in rows:
                value=row.string
                ip=str(value)

            CurrentIP=ip
            
            localtime = time.asctime( time.localtime(time.time()) )
            
            logfile=open(self.LogPath,'a')
            logfile.write(localtime+" , "+"Failed to reach target site: [ "+TargetWebsite+" ]"+" with current IP : "+CurrentIP+'\n')
            logfile.close()
            print("Webdriver cannot be operated properly with current IP : {IP} !!".format(IP=CurrentIP))

        sleep(2)
        

    #    if (ButtonName=="XLS"):
     #       NEXT_BUTTON_XPATH1 = '//input[@type="button" and @value="匯出XLS"]'#
      #      browser.find_element_by_xpath(NEXT_BUTTON_XPATH1).click()
        
       # elif(ButtonName=="HTML"):
        #    NEXT_BUTTON_XPATH2 = '//input[@type="button" and @value="匯出HTML"]'
         #   browser.find_element_by_xpath(NEXT_BUTTON_XPATH2).click()

       # else:
        #    return 0
            
        

        browser.close()
        browser.quit()

        return None

    def ParseHtmlTable(self, htmlFilePath="", updcsv=True, resetcsv=False):

        Tables=["BuySaleDetail.html",                #1
                "MarginDetail.html",                 #2
                "DayTrading.html",                   #3
                "EquityDistributionCatHis.html",     #4
                "EquityDistributionClassHis.html",   #5
                "DirectorShareholdDetail.html",      #6
                "EquityTransfer.html",               #7
                "K_Chart.html",                      #8
                "K_ChartCompare.html",               #9
                "K_ChartFlow.html",                  #10
                "StockList.html"
                ]

        TableName=""

        for nm in Tables:            
            if ( nm in htmlFilePath):                
                TableName=nm
        
                
        
        container=os.path.abspath( os.path.dirname(htmlFilePath) ) #
        #print(  os.path.join(container, "K_Chart.csv")   )
#============================================================================================================================================        
        if (TableName in ["BuySaleDetail.html", "MarginDetail.html", "DayTrading.html", "EquityDistributionCatHis.html", "EquityDistributionClassHis.html",
                          "DirectorShareholdDetail.html", "EquityTransfer.html", "K_Chart.html","K_ChartCompare.html","K_ChartFlow.html"]):
            

            
            skipRow=0
            
            f=open( htmlFilePath , 'br')#, encoding='UTF-8')
            lines=f.readlines()
            f.close()
            
            lines=lines[0].decode()#str(lines[0])#.encode())
            #print(lines)
            soup = BeautifulSoup(lines, 'html.parser')
            rows=soup.find_all("tbody")

            content=[]

            for row in rows:
                #print(str(row))
                soup2=BeautifulSoup(str(row),'html.parser')
                rows_tr=soup2.find_all("tr")
                for r_tr in rows_tr:
                    
                    #print(str(r_tr))
                    #print("===========================")
                    soup3=BeautifulSoup(str(r_tr),"html.parser")
                    entries=soup3.find_all("td")
                    
                    #print(len(entries))
                    r=""
                    for count_entry in range(len(entries)):
                        entry=entries[count_entry].string                        
                        #print("-",str(entry))
                        
                        #entry=entry.string
                        
                        if (count_entry==0 and TableName=="BuySaleDetail.html"):#Standardize time format  #1
                            Year=str(int(entry[0:2])+2000)+"-"#.replace("\\'", '')
                            Date=str(entry[-5:]).replace("/","-")
                            entry=Year+Date   
                            r=r+entry+','
                            
                        elif (count_entry==0 and (TableName=="MarginDetail.html" or TableName=="DirectorShareholdDetail.html" or TableName=="K_ChartCompare.html")):#2  #6
                            Time=entry.string
                            entry=Time.replace("/","-")
                            r=r+entry+','
                            
                        elif (count_entry==0 and TableName=="DayTrading.html"):#3
                            Time=entry.string
                            entry=str(date.today().year)+"-"+Time.replace("/","-")
                            r=r+entry+','

                        elif (count_entry==0 and TableName=="EquityDistributionCatHis.html"): #4                           
                            entry=entry.string                            
                            r=r+entry+','
                            
                        elif (count_entry==0 and TableName=="EquityDistributionClassHis.html"):#5
                            Time=entry.string
                            t=Time.split('M')
                            year=int(t[0])+2000
                            if (year>date.today().year):
                                year=int(t[0])+1900
                            Year=str(year)
                            entry=Year+"-"+t[1]
                            
                            r=r+entry+','
                            
                           
                        elif ((count_entry==0 or count_entry==5) and TableName=="EquityTransfer.html"):#7
                            Time=entry.string
                            entry=Time.replace("/","-")
                            
                            r=r+entry+','

                            
                        elif (count_entry==0 and TableName=="K_Chart.html"):
                            Time=entry.string
                            Date=Time.replace("/","-")
                            Year=str(date.today().year)
                            entry=Year+"-"+Date
                            
                            r=r+entry+','  

                        elif (count_entry==0 and TableName=="K_ChartFlow.html"):
                            Time=entry.string
                            Year=str(2000+int(Time[1:3]))
                            Date=Time.replace("W"+Time[1:3],"W")
                            
                            entry=Year+"-"+Date
                            
                            r=r+entry+','
                            
                    
                        elif (count_entry==0 and TableName=="gdgkdbkdjbjkrkhrxkdbkbdkjbbdkdbkdb"):
                            Time=entry.string
                            entry=Time.replace("/","-")
                            
                            r=r+entry+','
                            
                        else:                            
                            if (str(entry)!='None'):
                                r=r+str(entry).replace(',', '')+','
                            else:
                                r=r+'nan'+','
                    r=r+'\n'
                    content.append(r)

            if(updcsv==True):
                tnm=TableName.split('.')
                
                oldcsv=open(os.path.join(container, tnm[0]+"_xnunuxnuuru.csv"),'r')
                oldcontent=oldcsv.readlines()
                oldcsv.close()

                content_upd=[]
                for c in content:
                    content_upd.append(c)
                              
                count=0                                
                for oc in oldcontent:
                    ocl=oc.split(',')
                    timestamp_oldfile=ocl[0]
                    
                    savedata=True
                    
                    for c in content:
                        cl=c.split(',')
                        timestamp_newfile=cl[0]
                        
                        if(timestamp_newfile==timestamp_oldfile):
                            savedata=False
                            break
                        
                    if(savedata==True):
                        content_upd.append(oc)

                    count+=1



                    
                cf=open(os.path.join(container, tnm[0]+"_upd.csv"), 'w')
                for l in content_upd:
                    cf.write(l)

                    print(l)#len(l.split(',')))
                    #print("===============================")
                cf.close()
                
            elif(resetcsv==True):
                cf=open(os.path.join(container, tnm[0]+"_xnunuxnuuru.csv"), 'w')                
                count=0
                for c in content:
                    
                    if(True):
                        cf.write(c)
                    #print(c)#len(c.split(',')))
                    #print("===============================")
                    count+=1
                
                cf.close()
#============================================================================================================================================useless
        elif (TableName=="StockList.html"):
            tnm=TableName.split('.')
            
            f=codecs.open( htmlFilePath ,  'br')# 'r', encoding = 'utf8')#
            lines=f.readlines()
            f.close()

            
            lines=lines[0].decode()
            #lines=str(lines[0].encode())
            
            soup = BeautifulSoup(lines, 'html.parser')
            rows=soup.find_all("tr")

            content=[]

            for row in rows:
                soup2=BeautifulSoup(str(row), 'html.parser')#str(row).encode()
                entries=soup2.find_all("td")

                #print(str(row).encode())
                
                r=""           
                for entry in entries:
                    entry=entry.string
                    #entry=entry.encode().decode()
                    #print(entry)
                    
                    if (str(entry)!='None'):
                        r=r+str(entry).replace(',', '')+','
                    else:
                        r=r+'nan'+','
                r=r+'\n'#'\r\n'
                

                #print(r)
                

                #content.append(r.encode())
                content.append(r)
            
            if(updcsv==True):
                tnm=TableName.split('.')
                cf=open(os.path.join(container, tnm[0]+"_xnunuxnuuru.csv"), 'w', encoding='utf8')
                
                count=0
                for c in content:
                    cf.write(c.encode('UTF-8').decode('UTF-8'))
                    #print(c)#len(c.split(',')))
                    #print(count,"===============================")
                    count+=1
                    
                cf.close()
                    
            #file=open("Downloads\\StockList_xnunuxnuuru.csv",'br')
            #context=file.readlines()
            #file.close()

            #for c in context:
             #   print(c.decode('UTF-8'))
                
                               
               
                
        
            

#============================================================================================================================================





        elif TableName=="":

            return 0
        else:
            return 0

        return None


#=================================================================================================================================================
    def ParseTFsETable():
        return 0
'''   
localtime = time.asctime( time.localtime(time.time()) )
Year=date.today().year
Month=date.today().month
Day=date.today().day
filename="Downloads\\Futures_{year}-{month}-{day}.csv".format(year=Year,month=Month,day=Day)
fw=open(filename,'w')
localtime = time.asctime( time.localtime(time.time()) )

req = requests.get("http://www.taifex.com.tw/chinese/3/7_8.asp")
soup = BeautifulSoup(req.content, 'html.parser')
rows_form=soup.find_all("form")

soup2=BeautifulSoup( str(rows_form[1]), 'html.parser')#str(r1.encode())
rows_tr=soup2.find_all("tr")


entries=[]


skipRow=10

count=0
for r1 in rows_tr:#10 begin
    if count>skipRow-1:
        #print(count,"--------------------------------------------------------------------")
        soup3=BeautifulSoup( str(r1), 'html.parser')
        rows_div=soup3.find_all("div")
        
        r=""
        for d2 in rows_div:
            dd=str(d2).replace('<br/>',"")
            
            soup4=BeautifulSoup(dd,'html.parser')
            dvalue=soup4.find_all("div")

            value=str(dvalue[0].string)
            value=value.replace('\t',"")
            value=value.replace('\n',"")
            value=value.replace(' ',"")
            value=value.replace(',',"")
            
            #print('-',value.split('\r'),'-')

            
                
           
                

            #for l in value.split('\r'):
             #   fw.write(l+',')
                
            #fw.write('\n')
            for v in value.split('\r'):
                if v !="":
                    r=r+v+','
        #r=r+'\n'
                
        
        rw=""
        a=r.split(',')
        if (count<13):
            
            
            if count==10:                
                itemName=a[0]
                rw+=itemName
                
                
            elif count==11:
                timestamp=a[0]+"-"+a[1]
                rw=rw+timestamp+','
                for i_e in range(len(a)):
                    if (i_e>1 and a[i_e]!=""):
                        rw=rw+a[i_e]+','
                

            else:
                total="所有契約"
                rw=rw+total+','
                for i_e in range(len(a)):
                    if(a[i_e]!=""):
                        rw=rw+a[i_e]+','
                rw+='\n'
                
           
        else:
            if(count%2==1):
                itemName=a[0]+'\n'
                rw+=itemName
                
                timestamp=a[1]+'-'+a[2]
                rw=rw+timestamp+','
                for i_e in range(len(a)):
                    if (i_e>2 and a[i_e]!=""):
                        rw=rw+a[i_e]+','
            else:
                total="所有契約"
                rw=rw+total+','
                for i_e in range(len(a)):
                    if(a[i_e]!=""):                        
                        rw=rw+a[i_e]+','
                rw+='\n'

        rw+='\n'
        print(len(rw.split(',')),rw.split(','))
        fw.write(rw)
        #print(count,"--------------------------------------------------------------------")
        
    count+=1
fw.close()

'''
#=================================================================================================================================================
'''



with open(r"K_ChartFlow.html", "r",encoding = 'utf8') as f:
    page = f.read()
tree = html.fromstring(page)

#html = etree.parse("K_ChartFlow.html")
result = etree.tostring(tree, pretty_print=True)
print(result)

#==================
TargetWebsite="http://goodinfo.tw/StockInfo/ShowK_ChartFlow.asp?RPT_CAT=DR_6M&STOCK_ID=0881&CHT_CAT=WEEK"
ap=apophis(TargetWebsite)

ap.ParseHtmlTable("Downloads\\K_Chart.html",updcsv=True)


'''



#=================================================================================================================================================
'''
#TargetWebsite="http://goodinfo.tw/StockInfo/ShowK_ChartFlow.asp?RPT_CAT=DR_6M&STOCK_ID=0881&CHT_CAT=WEEK"#"http://goodinfo.tw/StockInfo/ShowK_Chart.asp?STOCK_ID=1303&CHT_CAT2=DATE"         "http://goodinf.tw/StockInfo/ShowK_ChartFlow.asp?RPT_CAT=DR_6M&STOCK_ID=0881&CHT_CAT=WEEK"   
TargetWebsite="http://www.taifex.com.tw/chinese/3/7_8.asp"
DownloadPath="Downloads"#"DataCollection\\Economy\\TW\\StockMarket\\1303\\K_Chart_data"#"D:\\DataCollection"   "F:\\workshop\\DataCollection\\1303"  "C:\\Users\\vamdo\\Documents\\Ldg\\Apophis\\DataCollection\\Economy\\TW\\StockMarket\\1303\\K_Chart_data"
WebDriverPath="BrowserDrivers\\Chrome\\chromedriver.exe"


options = webdriver.ChromeOptions()
prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': os.path.abspath(DownloadPath)}#修改下載目的資料夾
options.add_experimental_option('prefs', prefs)

browser = webdriver.Chrome(executable_path = os.path.abspath( WebDriverPath ) , chrome_options=options)
browser.get(  TargetWebsite  )#url



#NEXT_BUTTON_XPATH1 = '//input[@type="button" and @value="匯出XLS"]'#
#browser.find_element_by_xpath(NEXT_BUTTON_XPATH1).click()


sleep(10)

browser.close()
browser.quit()
'''
#=================================================================================================================================================
'''
TargetWebsite="http://goodinfo.tw/StockInfo/ShowK_ChartFlow.asp?RPT_CAT=DR_6M&STOCK_ID=0881&CHT_CAT=WEEK"#"http://goodinfo.tw/StockInfo/ShowK_Chart.asp?STOCK_ID=1303&CHT_CAT2=DATE"            
#TargetWebsite="http://goodinf.tw/StockInfo/ShowK_ChartFlow.asp?RPT_CAT=DR_6M&STOCK_ID=0881&CHT_CAT=WEEK"
DownloadPath="Downloads"#"DataCollection\\Economy\\TW\\StockMarket\\1303\\K_Chart_data"#"D:\\DataCollection"   "F:\\workshop\\DataCollection\\1303"  "C:\\Users\\vamdo\\Documents\\Ldg\\Apophis\\DataCollection\\Economy\\TW\\StockMarket\\1303\\K_Chart_data"


ap=apophis(TargetWebsite)
ap.RegularDownloadFiles("匯出HTML", DownloadPath)




#content=ap.ParseHtmlTrue)
#content=ap.ParseTop500Html(gencsv=True)

'''

#=================================================================================================================================================
'''
f=codecs.open("K_ChartFlow.xls",'r','utf-8')
lines=f.readlines()
f.close()

f=open( "DataCollection\\Economy\\TW\\StockMarket\\Top500\\StockList.html" , 'r', encoding = 'utf8')
lines=f.readlines()
f.close()

o=open("DataCollection\\Economy\\TW\\StockMarket\\Top500\\500list.txt",'w')
for line in lines:
    print (line)
'''

#=================================================================================================================================================        
'''
f=open( "K_Chart.html", 'r', encoding = 'utf8')#          "memo.txt"   
lines=f.readlines()
f.close()
#print(len(lines))
lines=str(lines[0].encode())
#for line in lines:
 #   print(line.encode())
soup = BeautifulSoup(lines, 'html.parser')
#print(soup.prettify())#print(soup.)
tr=soup.find_all("tr")
print("#cde2e5" in str(tr[0]))
print("自營" in str(tr[1]))
#for line in 
print(tr[2].encode('utf8'))


soup2=BeautifulSoup(str(tr[2]), 'html.parser')
td=soup2.find_all("nobr")
#=================================================================================================================================================


TargetWebsite="http://goodinfo.tw/StockInfo/ShowK_Chart.asp?STOCK_ID=1303&CHT_CAT2=DATE"
DownloadPath="F:\\workshop\\DataCollection\\1303"#"D:\\DataCollection"   "F:\\workshop\\DataCollection\\1303"  
#WebDriverPath="C:\\Users\\vamdo\\Documents\\Ldg\\Apophis\\chromedriver.exe"

ap=apophis(TargetWebsite)
ap.RegularDownloadFiles("XLS", DownloadPath)
ap.RegularDownloadFiles("HTML", DownloadPath)
#=================================================================================================================================================





'''
