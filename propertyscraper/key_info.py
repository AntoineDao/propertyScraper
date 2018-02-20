import requests
from bs4 import BeautifulSoup
import re
import datetime
from dateutil.parser import parse

class KeyInfo():
    
    def __init__(self, rent = None, date_available = None, deposit = None, letting_type = None, furnishing = None, epc = None, council_tax_band = None, insurrance_cost = None, energy_cost = None, water_cost = None, council_tax_cost = None):

        self.rent = float(re.sub(",","",rent)) if rent != None else None
        self.date_available = date_available
        self.deposit = float(re.sub(",","",deposit)) if deposit != None else None
        self.letting_type = letting_type
        self.furnishing = furnishing
        self.epc = epc
        self.council_tax_band = council_tax_band
        self.insurrance_cost = float(insurrance_cost) if insurrance_cost != None else None
        self.energy_cost = float(energy_cost) if energy_cost != None else None
        self.water_cost = float(water_cost) if water_cost != None else None
        self.council_tax_cost = float(council_tax_cost) if council_tax_cost != None else None
        
    @classmethod
    def from_json(cls, rec_json):
        return cls(rent = rec_json["rent"], date_available = rec_json["date_available"], deposit = rec_json["deposit"], letting_type = rec_json["letting_type"], furnishing = rec_json["furnishing"], epc = rec_json["epc"], council_tax_band = rec_json["council_tax_band"], insurrance_cost = rec_json["running_costs"][""], energy_cost = rec_json["running_costs"]["energy"], water_cost = rec_json["running_costs"]["water"], council_tax_cost = rec_json["running_costs"]["council_tax"])
        
    
    @classmethod
    def from_rightmove(cls, soup):
        rent = re.findall("\d+", soup.find("p", {"id":"propertyHeaderPrice"}).getText())[0]
        info_div =  soup.find("div", {"id": "lettingInformation"})
        info_table = info_div.find_all("tr")
        
        date_available = None
        deposit = None
        furnishing = None
        letting_type = None
        
        for row in info_table:
            key_value = row.find_all("td")
            key = key_value[0].getText().split(":")[0]
            value = key_value[1].getText()
            if key == "Date available":
                date_available = value
            elif key == "Deposit":
                deposit = value[1:]
            elif key == "Furnishing":
                furnishing = value
            elif key == "Letting type":
                letting_type = value
        
        return cls(rent = rent, date_available = date_available, deposit = deposit, furnishing = furnishing, letting_type = letting_type)
    
    @classmethod
    def from_zoopla(cls, soup):
        info = cls()
        
        rent = re.sub("\s", "", soup.find("div", {"class":"listing-details-price"}).getText()).split("pcm")[0].split("£")[1]
        info = soup.find("h3", string="Property info").next_sibling.next_sibling.find_all("li")
        date_available = None
        furnishing = None
        for element in info:
            element = element.getText()
            if "Available " in element:
                if "immediately" in element:
                    date_available = datetime.datetime.now()
                elif "Available from " in element:
                    date_available = re.sub("Available from ", "", element)
                    date_available = parse(date_available)
                date_available = date_available.strftime("%d/%m/%Y")
            elif "furnished" in element.lower():
                furnishing = element.lower()
        
        try:
            insurrance_cost = re.sub("£", "", soup.find("button", {"data-rc-name": "Insurance"}).find("span", {"rc-option-btn-price"}).getText())
        except:
            insurrance_cost = None
           
        try:
            energy_cost = re.sub("£", "", soup.find("button", {"data-rc-name": "Energy"}).find("span", {"rc-option-btn-price"}).getText())
        except:
            energy_cost = None
           
        try:
            water_cost = re.sub("£", "", soup.find("button", {"data-rc-name": "Water"}).find("span", {"rc-option-btn-price"}).getText())
        except:
            water_cost = None
           
        try:
            council_tax_cost  = re.sub("£", "", soup.find("button", {"data-rc-name": "Council Tax"}).find("span", {"rc-option-btn-price"}).getText())
        except:
            council_tax_cost = None
                
        return cls(rent = rent, date_available = date_available, furnishing = furnishing, insurrance_cost = insurrance_cost, energy_cost = energy_cost, water_cost = water_cost, council_tax_cost = council_tax_cost)
    
    @classmethod
    def from_gumtree(cls, soup):
        rent = soup.find("meta", {"itemprop": "price"})["content"]

        if "pm" in rent:
            rent = float(re.sub("pm", "", rent))
        elif "pw" in rent:
            rent = 4 * float(re.sub("pw","",rent))
        else:
            rent = None
        
        date_available = parse(soup.find("dl", {"class": "dl-attribute-list"}).find_all("dd")[-1].getText())
        date_available = date_available.strftime("%d/%m/%Y")
        
        return cls(rent = str(rent), date_available = date_available)
                
    def to_json(self):
        return {
            "rent": self.rent,
            "date_available": self.date_available,
            "deposit": self.deposit,
            "letting_type": self.letting_type,
            "furnishing": self.furnishing,
            "epc": self.epc,
            "council_tax": self.council_tax_band,
            "running_costs": 
            {
                "insurrance": self.insurrance_cost,
                "energy": self.energy_cost,
                "water": self.water_cost,
                "council_tax": self.council_tax_cost
            }
        }
