from urllib.parse import urlencode
from scrapy.utils.response import open_in_browser
from scrapy.http import Request, FormRequest

import scrapy
from ..items import OriasItem


class OriasSpider(scrapy.Spider):
    name = "orias"

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
        '_ifp': 'on',
        'submit': 'Search'
    }

    global_count = 1
    start_at_page = 1

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
        print(f"Page : {self.global_count}")
        if self.global_count < self.start_at_page:
            self.global_count += 3
            number = "{:,}".format(self.global_count).replace(",", "\xa0")
            url = response.css("span.pagelinks").xpath(f"a[text()='{number}']/@href").get()
            if url is not None:
                print(f"Page (avance rapide) : {self.global_count}")
                yield Request(url, callback=self.parse_menu)
            else:
                self.save_page(response, "last_page")
        else:
            for elem in response.css("table tr")[1:]:
                url = elem.css("td")[2].css("a::attr(href)")[0].extract().strip()
                yield Request(url,
                              callback=self.parse_data,
                              dont_filter=True,
                              priority=2)

            url = response.css("span.pagelinks a img[alt='Suivant']").xpath('../@href').get()
            if url is not None and self.global_count < 10:
                self.global_count += 1
                yield Request(url, callback=self.parse_menu)
            else:
                self.save_page(response, "last_page")

    def parse_data(self, response):
        final_dict = {}
        # Infos global
        if len(response.css("#mainint div")) >= 1:
            for dt in response.css("#mainint div")[0].css("dt"):
                dt_value = dt.css('::text').get()
                if dt.xpath('./following-sibling::dd'):
                    dd_value = dt.xpath('./following-sibling::dd')[0].xpath('normalize-space(./text())').get()
                    final_dict[dt_value] = dd_value

        # Adresses
        for dt in response.css("#intermediaryCoordinate2").css("dt"):
            dt_value = dt.css('::text').get()
            if dt.xpath('./following-sibling::dd'):
                dd_value = dt.xpath('./following-sibling::dd')[0].xpath('normalize-space(./text())').get()

                while dt_value in final_dict:
                    dt_value = dt_value + "_bis"
                final_dict[dt_value] = dd_value

        mandataire = []
        for categ in response.css('#mainint div.row-fluid div.intermediaryRegistrations'):
            for sub_categ in categ.css('div.row-fluid div div.blocint3'):
                dict_mandataire = {}
                if categ.css('h2::text').get():
                    dict_mandataire["categ"] = categ.css('h2::text').get().strip()
                if sub_categ.css('div.header::text').get():
                    dict_mandataire["sub_categ"] = sub_categ.css('div.header::text').get().strip()
                if sub_categ.css('div.header span::text').get():
                    dict_mandataire["type"] = sub_categ.css('div.header span::text').get().strip()
                if sub_categ.css('dl dd::text').get():
                    dict_mandataire["date"] = sub_categ.css('dl dd::text').get().strip()

                mandataire.append(dict_mandataire)

        final_dict['mandataire'] = mandataire

        yield final_dict

    def save_page(self, response, name="page"):
        print('Save page!')
        filename = f'data/{name}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

        open_in_browser(response)
