# -*- coding: utf-8 -*-
"""
Created on Sat May 29 15:01:06 2021

@author: Sabeer_K
"""
from abc import ABC, abstractmethod
import json
from datetime import date, timedelta, datetime
import os 
import sys
import requests
import time

MAX_RANGE_IN_DAYS = 3 #query checks availability up to this day from now

url_find_by_pin = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin"
this_path = os.path.abspath(__file__).rsplit(os.sep, 1)[0]
area_config_file = os.path.join(this_path, "vaccine_data_v1.json")


class Criteria:   
    def __init__(self,ageLimit=18, dose1=True, dose2=False):
        self.ageLimit = ageLimit
        self.dose1 = dose1
        self.dose2 = dose2    
        
    def doesMatch(self, vaccineData):
        if(vaccineData['min_age_limit'] == self.ageLimit and 
           ((self.dose1 & vaccineData['available_capacity_dose1'] > 0) or 
           (self.dose2 & vaccineData['available_capacity_dose2'] > 0))):
            return True
        return False

class Notifier(ABC):
    @abstractmethod
    def notify(self,msg):
        pass
class TelegramNotifier(Notifier):
    def __init__(self,botChatID,groupChatID,botToken):
        self.botChatID = botChatID
        self.groupChatID = groupChatID
        self.botToken = botToken
    def notify(self,msg):
        print(msg)
        send_text = 'https://api.telegram.org/bot' + self.botToken + '/sendMessage?chat_id=' + self.groupChatID  + '&parse_mode=Markdown&text=' + msg
        response = requests.get(send_text)
        print(response.json())
        return response.json()
        
    
class AreaConfig:
    def __init__(self,pincodes, notifier,info, ageLimit=18, dose1=True, dose2=False):
        self.pincodes = pincodes
        self.criteria = Criteria(ageLimit,dose1,dose2)
        self.notifier = notifier
        self.info = info
        self.sharedAlerts = {}
        
    def getPincodes(self):
        return self.pincodes
    
    def processData(self, vaccineData):
        if(self.criteria.doesMatch(vaccineData)):
            i = vaccineData
            cuur_hour = datetime.now().hour
            mes_key = "{0}_{1}_{2}_{3}_{4}_{5}".format(i['pincode'], i['min_age_limit'], i['name'],i['fee_type'],i['vaccine'],cuur_hour)
            if mes_key not in self.sharedAlerts:
                mes = "Pincode: {0}, Min Age: {1}, Name: {2}, Addr: {3}, FeeType: {4}, Avl Dose1: {5}, Avl Dose2: {6}, Vaccine: {7}, Data: {8}".format(
                        i['pincode'], i['min_age_limit'], i['name'], i['address'], i['fee_type'], 
                        i['available_capacity_dose1'], i['available_capacity_dose2'], i['vaccine'], i['date']) 
                self.notifier.notify(mes)
                self.sharedAlerts[mes_key] = 1
    def notifyConfigInfo(self):
        message = ("%s , AgeLimit: %d, Dose1: %s, Dose2: %s, Pinodes: %s" 
                   % (self.info, self.criteria.ageLimit, str(self.criteria.dose1),
                      str(self.criteria.dose2),str(self.pincodes)))
        self.notifier.notify(message)
        
class AvailabilityChecker:
    def __init__(self, areaConfigs):
        self.areaConfigs = areaConfigs
        self.updatePincodes()
    def updatePincodes(self):
        self.pincodes = []
        for areaConfig in self.areaConfigs:
            self.pincodes = self.pincodes + list(set(areaConfig.pincodes) - set(self.pincodes))
    def generateWebQuries(self):
        self.webQueries = []
        for i in range(0, MAX_RANGE_IN_DAYS):
            now = (date.today() + timedelta(days=i)).strftime("%d-%m-%y")
            for pincode in self.pincodes: 
                URL = "{0}?pincode={1}&date={2}".format(url_find_by_pin,pincode,now)
                #print(URL)
                self.webQueries.append(URL)
    def processQuries(self):
        self.generateWebQuries()
        for URL in self.webQueries:
            r = requests.get(url=URL)
            data = r.json()
            #print(data)
            if data['sessions']:
                for i in data['sessions']:
                    if(i['available_capacity_dose1'] > 0 or i['available_capacity_dose2'] > 0):
                        for areaConfig in self.areaConfigs:
                            areaConfig.processData(i)
                        
        
def getAreaConfigs():
    areaConfigsL = []
    with open(area_config_file,'r') as fHandle:
        areaConfigs = json.load(fHandle)
        for conf in areaConfigs:
            try:
                info = conf
                areaData = areaConfigs[conf]
                ageLimit = areaData['AgeLimit']
                notifier = TelegramNotifier(areaData['botChatID'],areaData['groupChatID'], areaData['botToken'])
                areaConfig = AreaConfig(areaData['Pincodes'], notifier,info, ageLimit, areaData['Dose1'], areaData['Dose2'])
                #areaConfig.notifyConfigInfo()
                areaConfigsL.append(areaConfig)
            except:
                print(sys.exc_info()[0])
    return areaConfigsL
    
if __name__ == "__main__":
    print('Vaccine availability checker starts...')
    areaConfigs =  getAreaConfigs()
    print("No of configs found: "+str(len(areaConfigs)))
    print(type(areaConfigs))
    for areaConfig in areaConfigs:
        areaConfig.notifyConfigInfo()
    avlbChecker = AvailabilityChecker(areaConfigs)
    avlbChecker.processQuries()
    while True:
        try:
            avlbChecker.processQuries()
        except:
            print(sys.exc_info()[0])
        time.sleep(1)
               
    