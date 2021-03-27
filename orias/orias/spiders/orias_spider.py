from urllib.parse import urlencode
from scrapy.utils.response import open_in_browser
from scrapy.http import Request, FormRequest
import scrapy


class OriasSpider(scrapy.Spider):
    name = "orias"

    global_count = 0

    start_urls = [
        'https://www.orias.fr/search'
    ]

    BASE_URL = "https://www.orias.fr"

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Referer': 'https://www.orias.fr/web/guest/search'
    }

    params = {'p_p_id': 'intermediaryDetailedSearch_WAR_oriasportlet',
              'p_p_lifecycle': '0',
              'p_p_state': 'normal',
              'p_p_mode': 'view',
              'p_p_col_id': 'column-1',
              'p_p_col_count': '1',
              '_intermediaryDetailedSearch_WAR_oriasportlet_d-16544-p': '1',
              '_intermediaryDetailedSearch_WAR_oriasportlet_implicitModel': 'true',
              '_intermediaryDetailedSearch_WAR_oriasportlet_spring_render': 'searchResult',
              }

    data = {
        'searchString': '',
        'address': '',
        'zipCodeOrCity': '',
        '_coa': 'on',
        '_aga': 'on',
        '_ma': 'on',
        '_mia': 'on',
        '_euIAS': 'on',
        'mandatorDenomination': '',
        'wantsMandator': 'no',
        '_cobsp': 'on',
        '_mobspl': 'on',
        '_mobsp': 'on',
        '_miobsp': 'on',
        '_bankActivities': '1',
        '_euIOBSP': 'on',
        '_cif': 'on',
        '_alpsi': 'on',
        '_cip': 'on',
        'ifp': 'true',
        '_ifp': 'on',
        'submit': 'Search'
    }

    def start_requests(self):
        request = Request(self.BASE_URL, callback=self.parse_search)
        return [request]

    def parse_search(self, response):
        url = f'{self.BASE_URL}/search?{urlencode(self.params)}'
        request = FormRequest(url,
                              callback=self.parse_menu,
                              headers=self.headers,
                              formdata=self.data)
        request.meta['params'] = self.params
        return [request]

    def parse_menu(self, response):
        for elem in response.css("table tr")[1:4]:
            url = elem.css("td")[2].css("a::attr(href)")[0].extract().strip()
            yield Request(url,
                          callback=self.parse_data,
                          dont_filter=True,
                          priority=2)

        self.global_count = self.global_count + 1
        if self.global_count <= 1:
            url = response.css("span.pagelinks a img[alt=Suivant]").xpath('../@href').get()
            if url is not None:
                yield Request(url, callback=self.parse_menu)

    def parse_data(self, response):
        print("New page !")

        final_dict = {}
        for dt in response.css("#mainint dt"):
            dt_value = dt.css('::text').get()
            dd_value = dt.xpath('./following-sibling::dd/text()').get()
            final_dict[dt_value] = dd_value
        yield final_dict

    def save_page(self, response):
        print('save_page')
        filename = 'data/page2.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

        open_in_browser(response)


"""    def parse(self, response):
        print("Parse !!!")
        url = "https://www.orias.fr/search"
        #url = "https://www.orias.fr/search?p_p_id=intermediaryDetailedSearch_WAR_oriasportlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&_intermediaryDetailedSearch_WAR_oriasportlet_myaction=fullSearch"
        Request(url, callback=self.save_page, headers=self.headers, meta=self.params)"""


"""    def start_requests(self):
        url = f'{self.BASE_URL}/search/?{urlencode(self.params)}'
        request = scrapy.Request(url, callback=self.save_page)
        request.meta['params'] = self.params
        return [request]"""


"""    def start_requests(self):
        url = "https://www.orias.fr/search?" + urlencode(self.params)
        yield scrapy.http.Request(url,
                                  callback=self.save_page,
                                  headers=self.headers)"""


"""        author_page_links = response.css('.author + a')
        yield from response.follow_all(author_page_links, self.parse_author)

        pagination_links = response.css('li.next a')
        yield from response.follow_all(pagination_links, self.parse)

    def parse_author(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        yield {
            'name': extract_with_css('h3.author-title::text'),
            'birthdate': extract_with_css('.author-born-date::text'),
            'bio': extract_with_css('.author-description::text'),
        }"""


"""    def parse(self, response):
        final_dict = {}
        for dt in response.css("#mainint dt"):
            dt_value = dt.css('::text').get()
            # Getting corresponding dd value
            dd_value = dt.xpath('./following-sibling::dd/text()').get()
            final_dict[dt_value] = dd_value
        yield final_dict"""


"""    def parse(self, response):
        for post in response.css("#mainint"):
            yield {
                'nom': post.css("dl.dl-horizontal")[0].css("dd")[0].css("dd::text").get().strip(),
                'prenom': post.css("dl.dl-horizontal")[0].css("dd")[1].css("dd::text").get().strip(),
                'immatriculation': post.css("dl.dl-horizontal")[1].css("dd")[0].css("dd::text").get().strip(),
                'siren': post.css("dl.dl-horizontal")[1].css("dd")[2].css("dd::text").get().strip(),
                'statut': post.css("dl.dl-horizontal")[1].css("dd")[3].css("dd::text").get().strip(),
                'code_naf': post.css("dl.dl-horizontal")[1].css("dd")[5].css("dd::text").get().strip()
            }"""


"""    def parse(self, response):
        page = response.url.split('/')[-1]
        filename = 'posts-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)"""
