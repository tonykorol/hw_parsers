import requests
import requests_html
import json


class BelTurism:
    session = requests_html.HTMLSession()
    BASE_URL = "https://belturizm.by/avtobusnie-turi/page/{}"
    ITEMS_ROOT = "#primary div.wte-category-outer-wrap"

    # primary > div > div.wp-travel-engine-archive-repeater-wrap > div.wte-category-outer-wrap > div.category-main-wrap.col-2.category-grid
    # "#primary div.category-main-wrap"
    # #primary > div > div.wp-travel-engine-archive-repeater-wrap > div.wte-category-outer-wrap

    def get_page(self, num=1):
        url = self.BASE_URL.format(num)
        response = self.session.get(url)
        if response.status_code == 200:
            return response
        raise RuntimeError(f"Failed status code {response.status_code}")

    def parse(self):
        # div.trip-pagination.pagination a:nth-child(5)
        page = self.get_page(1)
        last_num = page.html.find(f"{self.ITEMS_ROOT} .trip-pagination.pagination a:nth-child(5)", first=True)
        if last_num is not None:
            last_page_num = int(last_num.text.replace('Страница ', ''))
            return page, last_page_num
        else:
            print("No page found")
            return


    def save_result(self):
        page, last_page_num = self.parse()
        items_box = page.html.find(self.ITEMS_ROOT, first=True)
        result = []
        for num in range(2, last_page_num + 2):
            items = items_box.find("div.category-main-wrap.col-2.category-grid > div.category-trips-single")
            for item in items:
                item_data = {}
                url_box = item.find(".category-trip-fig > a", first=True)
                item_data["url"] = url_box.attrs["href"]
                img_box = item.find(".category-trip-fig img", first=True)
                item_data["img"] = img_box.attrs["src"]
                desc_box = item.find("h2", first=True)
                item_data["desc"] = desc_box.text
                cost_box = item.find(".wpte-price", first=True)
                item_data["cost"] = cost_box.text
                curr_box = item.find(".wpte-currency-code", first=True)
                item_data["curr"] = curr_box.text
                result.append(item_data)
            page = self.get_page(num)
            items_box = page.html.find(self.ITEMS_ROOT, first=True)
        return result

    def save(self):
        data = self.save_result()
        with open("bt_result.json", "w") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

#primary div.wte-category-outer-wrap > div.category-main-wrap.col-2.category-grid > div:nth-child(1)
# div.category-main-wrap.col-2.category-grid > .category-trips-single



class Wildberries:
    def __init__(self):
        self.url = "https://catalog.wb.ru/catalog/men_clothes1/v1/catalog"

    def get_data(self):
        response = requests.get(self.url, params={"cat": "8144", "limit": "100", "sort": "popular",
                                                  "page": "1", "appType": "128", "curr": "rub",
                                                  "lang": "ru", "dest": "-59208", "spp": "30"})
        if response.status_code == 200:
            return response.json()
        raise RuntimeError(f'Was status code {response.status_code}')

    def save(self):
        data = self.get_data()
        with open("wb_result.json", "w") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
# https://catalog.wb.ru/catalog/men_clothes1/v1/catalog?cat=8144&limit=100&sort=popular&page=1&appType=128&curr=byn&lang=ru&dest=-59208&spp=30


if __name__ == "__main__":
    WB = Wildberries()
    WB.save()

    BT = BelTurism()
    BT.save()
