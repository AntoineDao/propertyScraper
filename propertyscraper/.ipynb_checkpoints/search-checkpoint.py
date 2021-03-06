import requests
from bs4 import BeautifulSoup
from .accomodation import RentedAccomodation
import re

class RentedSearch():
    
    def __init__(self,link = None):
        self.link = link
        self.soup = BeautifulSoup(requests.get(self.link).content, 'html.parser')
        self.ids = list()
        self.hrefs = list()
        
    @classmethod
    def from_zoopla(cls, link):
        search = cls(link)
        for id in search.soup.find_all("li", {"class":"clearfix"}):
            try:
                search.ids.append(id["data-listing-id"])
            except:
                pass
        search.data = [RentedAccomodation.from_zoopla(id) for id in search.ids]
        return search
            
    @classmethod
    def from_rightmove(cls, link):
        search = cls(link)
        for id in search.soup.find_all("a", {"class": "propertyCard-anchor"}):
            id = re.sub("prop","",id["id"])
            search.ids.append(id) if len(id) == 8 else None
        search.data = [RentedAccomodation.from_rightmove(id) for id in search.ids]
        return search

    @classmethod
    def from_gumtree(cls, link):
        search = cls(link)
        for item in search.soup.find_all("li", {"class": "natural"}):
            href = "https://www.gumtree.com" + item.find("a",{"class":"listing-link"})["href"]
            id = href.split("/")[-1]
            search.hrefs.append(href)
            search.ids.append(id)
        search.data = [RentedAccomodation.from_gumtree(href) for href in search.hrefs]
        return search
            
