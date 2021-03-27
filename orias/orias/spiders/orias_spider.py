from urllib.parse import urlencode
from scrapy.utils.response import open_in_browser
from scrapy.http import Request, FormRequest
import scrapy


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
    start_at_page = 1730

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
            if url is not None:  # and self.global_count < 20:
                self.global_count += 1
                yield Request(url, callback=self.parse_menu)
            else:
                self.save_page(response, "last_page")

            print(f"Page : {self.global_count}")

    def parse_data(self, response):
        final_dict = {}
        for dt in response.css("#mainint dt"):
            dt_value = dt.css('::text').get()
            dd_value = dt.xpath('./following-sibling::dd/text()').get()

            if dt_value == "Date de suppression":
                categ = dt.xpath("..//..//div[@class='header']/text()").get()
                if categ is not None:
                    dt_value = dt_value + "_" + categ.strip()

            while dt_value in final_dict:
                dt_value = dt_value + "_bis"
            final_dict[dt_value] = dd_value
        yield final_dict

    def save_page(self, response, name="page"):
        print('Save page!')
        filename = f'data/{name}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

        open_in_browser(response)
