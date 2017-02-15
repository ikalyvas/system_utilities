import requests
import re
from time import sleep
from sys import exit


class Crawler:

    def __init__(self,url,max_pages):
        self.url = url
        self.mapping = {}
        self.sitemap = None
        self.max_pages = max_pages


    def fetch_page(self,page):
        try:
            print 'Getting %s' % page
            response = requests.get(page)
        except Exception as e:
            print 'Exception occured: %s\nError occured while fetching the page %s' % (str(e),page)
            return None
        else:
            print 'Returning content of %s' % page
            return response

        
    def construct_sitemap(self,page):

        print 'Constructing sitemap for %s' % page.url
        try:
            self.sitemap = set(re.findall(r'(?<=href=).+.html"',page.text))
        except:
            print 'Exception occured %s\nCould not construct sitemap for page %s' % page.url
            exit(2)
        else:
            print 'Constructed sitemap for %s' % page.url
            #print self.sitemap
            return [i.strip('"') for i in self.sitemap]

    def fetch_assets(self,response):

        print 'Getting assets from %s' % response.url
        try:
            self.img_assets = [ self.url + asset
                          for asset in re.findall(r'(?<=<img src=")assets.+?(?=")',response.text)
                          if 'http' not in asset
                        ]

            self.script_assets = [ self.url + asset
                             for asset in re.findall(r'(?:(?<=<script src=")|(?<=<script src=\')).+.js(?=\')',response.text)
                             if 'http' not in asset
                            ]
        
            self.link_assets = [ self.url + asset
                            for asset in re.findall(r'(?<=<link rel=).+(assets.+?)>',response.text)
                            if 'http' not in asset
                          ]
        
            self.href_assets = set(sorted(re.findall(r'(?<=<a href=)(.+?)">?',response.text)))

        except Exception as e:
            print 'Exception occured: %s\nCould not fetch assets from the page %s' % (str(e),response.url)

        else:
            print 'Updating total_assets from %s' % response.url
            self.total_assets = list(self.href_assets) +\
                                self.link_assets +\
                                self.img_assets +\
                                self.script_assets
            return self.total_assets


    def show_assets(self,sitemap,assets):
        print 'Showing Sitemap :'
        for site in sitemap:
            print site
        print '\n'*3
        print 'Showing Assets :'
        for asset in assets:
            print asset
            
    def crawl(self):

        num_of_links_visited = 0
        page_content = self.fetch_page(self.url)
        sitemaps = self.construct_sitemap(page_content)
        assets = self.fetch_assets(page_content)
        self.show_assets(sitemaps,assets)

        site = sitemaps[0]
        linksToVisit = sitemaps[1:]
        while num_of_links_visited < self.max_pages:

            sleep(3)
            print 'Visited so far %s links' % num_of_links_visited
            
            
            response = self.fetch_page(self.url+site)
            sitemap = self.construct_sitemap(response)
            for site in sitemap:
                if site not in linksToVisit:
                    linksToVisit = linksToVisit + [site]
            print 'Sitemap %s' % linksToVisit
            raw_input()
            assets = self.fetch_assets(response)
            print '\n'*2
            print 'Assets:' ,assets
            num_of_links_visited += 1
            
            print 'Visited %s links ' % num_of_links_visited
            site = linksToVisit[0]
            linksToVisit = linksToVisit[1:]



            


crawler = Crawler('http://www.yoyowallet.com/',20)
crawler.crawl()

