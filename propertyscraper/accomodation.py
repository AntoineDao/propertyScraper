import requests
from bs4 import BeautifulSoup
import re
from .address import Address
from .key_info import KeyInfo

class RentedAccomodation():

    def __init__(self, id  = None, href = None):
        self.type = "rented"
        self.id = str(id) if id != None else None
        self.title = None
        self.href = str(href) if href != None else None
        self.description = None
        self.tags = None
        self.source = None
        self.address = Address()
        self.key_info = KeyInfo()

    @classmethod
    def from_rightmove(cls, id):
        accom = cls(id = id)
        print("Fetchin property {} from Rightmove...".format(id))
        accom.href = "http://www.rightmove.co.uk/property-to-rent/property-" + accom.id + ".html"
        accom.soup = BeautifulSoup(requests.get(accom.href).content, "html.parser")
        print("Parsing property...")
	accom.title = accom.soup.find("h1", {"itemprop": "name"}).getText()

        accom.description = re.sub("\s", " ", accom.soup.find("p", {"itemprop":"description"}).getText())
        accom.description = re.sub(" +", " ", accom.description)[1:]
        try:
            accom.tags = [tag.getText() for tag in accom.soup.find("div", {"class": "key-features"}).find_all("li")]
        except:
            pass

        accom.address = Address.from_rightmove(accom.soup)

        accom.key_info = KeyInfo.from_rightmove(accom.soup)
        accom.source = "rightmove"
        print("Done!")
        return accom

    @classmethod
    def from_zoopla(cls, id):
        print("Fetching property {} from Zoopla...".format(id))
        accom = cls(id = id)
        accom.href = "https://www.zoopla.co.uk/to-rent/details/" + accom.id
        accom.soup = BeautifulSoup(requests.get(accom.href).content, "html.parser")
        print("Parsing property...")
        accom.title = accom.soup.find("h2", {"class": "listing-details-h1"}).getText()
        try:
            accom.description = re.sub("\s", " ", accom.soup.find("div", {"itemprop": "description"}).getText())
        except:
            pass
        try:
            accom.tags = [tag.getText() for tag in accom.soup.find("h3", string="Property features").next_sibling.next_sibling.find_all("li")]
        except:
            pass
        accom.address = Address.from_zoopla(accom.soup)
        accom.key_info = KeyInfo.from_zoopla(accom.soup)
        accom.source = "zoopla"
        print("Done!")
        return accom

    @classmethod
    def from_gumtree(cls, href):
        accom = cls(href = href)
        print("Fetching property from Gumtree...")
        accom.soup = BeautifulSoup(requests.get(accom.href).content, "html.parser")
        print("Parsing property...")
        accom.title = accom.soup.find("h1", {"id": "ad-title"}).getText()
        accom.description = re.sub("\s", " ", accom.soup.find("p", {"class": "ad-description"}).getText())
        accom.address = Address.from_gumtree(accom.soup)
        accom.key_info = KeyInfo.from_gumtree(accom.soup)
        accom.source = "gumtree"
        print("Done!")
        return accom

    def to_json(self):
        return {
            "title": self.title,
            "source": self.source,
            "href": self.href,
            "address": self.address.to_json(),
            "description": self.description,
            "key_info": self.key_info.to_json(),
            "tags": self.tags
        }
