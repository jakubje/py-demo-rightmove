import os
import csv
import json
import requests
import datetime
from bs4 import BeautifulSoup as bs

class PropertyScraper():
    def __init__(self):
        self.headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.rightmove.co.uk/property-to-rent/search.html?searchLocation=London&useLocationIdentifier=true&locationIdentifier=REGION%5E87490&rent=To+rent',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }
        self.count = 0
        self.properties = list()

    def setup(self):
        if not os.path.exists('data'):
            os.makedirs('data')


    def scrape(self):
        self.setup()
        
        while True:
            print(f"Scraping index... {self.count}")
            try:
                params = (
                    ('locationIdentifier', 'REGION^87490'),
                    ('searchType', 'RENT'),
                    ('maxBedrooms', '3'),
                    ('minBedrooms', '3'),
                    ('maxPrice', '3000'),
                    ('index', self.count),
                    ('propertyTypes', ''),
                    ('includeLetAgreed', 'false'),
                    ('mustHave', ''),
                    ('dontShow', ''),
                    ('furnishTypes', ''),
                    ('keywords', ''),
                )
                
                response = requests.get('https://www.rightmove.co.uk/property-to-rent/find.html', headers=self.headers, params=params)
                if response.status_code == 200:

                    self.count += 24

                    soup = bs(response.text, 'html.parser')
                    properties = soup.find_all("div",{"class": "l-searchResult is-list"})
                    totalPropertyCount = soup.find("div",{"id": "searchHeader"}).text.split(" ")[0].replace(",", "")

                    for property in properties:
                        self.properties.append(
                            {
                                'id': property['id'].split("-")[1],
                                'propertyLink': "https://www.rightmove.co.uk/properties/{}".format(property['id'].split("-")[1]),
                                'propertyImg' : property.find("img", {"alt": "Property Image 1"})['src'],
                                'propertyType' : property.find("h2", {"class": "propertyCard-title"}).text.strip(),
                                'propertyPrice' : property.find("span", {"class": "propertyCard-priceValue"}).text,
                                'address' : property.find("address", {"class": "propertyCard-address"}).text.strip(),
                                'addedDate' : property.find("div", {"class": "propertyCard-branchSummary"}).span.text,
                                'contactNumber' : property.find("a", {"class": "propertyCard-contactsPhoneNumber"}).text
                            }
                        )

                    totalPageCountIndex = round(int(totalPropertyCount)/24) * 24


                    if self.count >= totalPageCountIndex:
                        self.saveToCsvFile()
                        self.saveToJsonFile()
                        break

                elif response.status_code == 400:
                    print("Page Not Found")
                    self.saveToCsvFile()
                    self.saveToJsonFile()
                    break
                

            except Exception as e:
                print(e)

    def saveToJsonFile(self):
        with open('data/output.json', 'w', encoding='utf-8') as f:
            json.dump(self.properties, f, ensure_ascii=False, indent=4)

    def saveToCsvFile(self, header=True):
        filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(f"data/{filename}.csv", "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
            'Id',
            'Property Type',
            'Property Price',
            'Property Image',
            'Property Link',
            'Address',
            'Added Date',
            'Contact Number',
        ])
            if header:
                writer.writeheader()
            for item in self.properties:
                writer.writerow({
                    'Id': item['id'],
                    'Property Type': item['propertyType'],
                    'Property Price': item["propertyPrice"],
                    'Property Image': item["propertyImg"],
                    'Property Link': item["propertyLink"],
                    'Address': item["address"],
                    'Added Date': item["addedDate"],
                    'Contact Number': item["contactNumber"]
                }) 


scraper = PropertyScraper()
scraper.scrape()