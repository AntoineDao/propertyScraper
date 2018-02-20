import requests
from bs4 import BeautifulSoup
import re
import json
from .utilities import *

class Address():
    
    def __init__(self, postcode = None, street = None, latitude = None, longitude = None, city = None, area = None, tags = []):
        self.postcode = postcode
        self.street = street
        self.latitude = float(latitude) if latitude != None else None
        self.longitude = float(longitude) if longitude != None else None
        self.city = city
        self.area = area
        self.tags = tags
        
    @classmethod
    def from_json(cls, rec_json):
        addr = cls()
        postcode = rec_json["postcode"]
        street = rec_json["street"]
        latitude = rec_json["latitude"]
        longitude = rec_json["longitude"]
        city = rec_json["city"]
        area = rec_json["area"]
        tags = rec_json["tags"]
        return cls(postcode = postcode, street = street, lattitude = lattitude, longitude = longitude, city = city, area = area, tags = tags)
        
    @classmethod
    def from_rightmove(cls, soup):
        address_string = soup.find("address", {"itemprop": "address"}).getText()
        raw = re.sub("\s", " ", address_string)
        raw = re.sub(" +", " ", raw).split(",")
        
        tags = list()
        postcode = None
        street = None
        
        for item in raw:
            if re.match("[A-Z]{1,2}[0-9R]{1,2}", item[1:]):
                postcode = item[1:]
            elif "street" in item.lower():
                street = item[1:].title()
            else:
                tags.append(item[1:].title())
        
        return cls(postcode = postcode, street = street, tags = tags)
                
    @classmethod
    def from_zoopla(cls, soup):
        latitude = soup.find("meta", {"itemprop": "latitude"})["content"]
        longitude = soup.find("meta", {"itemprop": "longitude"})["content"]
        address_string = soup.find("h2", {"itemprop": "streetAddress"}).getText().split(", ")
        postcode = address_string[-1].split(" ")[-1]
        city = " ".join(address_string[-1].split(" ")[:-1])
        street = address_string[0]
        area = None
        if len(address_string)  == 3:
            area = address_string[1]
        
        return cls(latitude = latitude, longitude = longitude, postcode = postcode, city = city, street = street, area = area)
    
    @classmethod
    def from_gumtree(cls, soup):
        try:
            location_string = soup.find("div", {"class": "googlemap"})["data-googlemap"]
            latitude = float(between(location_string, "latitude:", ","))
            longitude = float(after(location_string, "longitude:"))
        except:
            latitude = None
            longitude = None
        tags = soup.find("span", {"itemprop": "address"}).getText().split(", ")
        return cls(latitude = latitude, longitude = longitude, tags = tags)
        
    def to_json(self):
        return {
        "postcode": self.postcode, 
        "street": self.street, 
        "latitude": self.latitude, 
        "longitude": self.longitude, 
        "city": self.city, 
        "area": self.area, 
        "tags": self.tags 
        }