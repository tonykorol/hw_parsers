import requests
import requests_html
import json
from abc import ABC, abstractmethod


class AbstractClass(ABC):
    @abstractmethod
    def _parse(self):
        ...


class Parser(AbstractClass):
    session = requests_html.HTMLSession()

    def __init__(self, url: str, **kwargs):
        self.result = None
        self.url = url
        self.kwargs = kwargs

    def _get_page(self, num):
        self.kwargs["params"]["page"] = num
        response = self.session.get(self.url, **self.kwargs)
        if response.status_code == 200:
            return response
        raise RuntimeError(f"Failed status code {response.status_code}")

    def _parse(self):
        pass

    def start(self):
        self.result = self._parse()

    def save(self):
        with open(f"{self.__class__.__name__}_result.json", "w") as file:
            json.dump(self.result, file, indent=4, ensure_ascii=False)


class AvBy(Parser):
    ITEMS_ROOT = "#__next div.listing > div > div:nth-child(3) > div"

    def _parse(self):
        num = 1
        result = []
        while True:
            page = self._get_page(num)
            items_box = page.html.find(self.ITEMS_ROOT, first=True)
            if items_box is None:
                return result
            items = items_box.find("div.listing-item")
            for item in items:
                item_data = {}
                url_box = item.find("div.listing-item__about > h3 > a", first=True)
                item_data["url"] = url_box.attrs["href"]
                img_box = item.find("div.listing-item__photo > img", first=True)
                if img_box is not None:
                    item_data["img"] = img_box.attrs["src"]
                else:
                    item_data["img"] = "No image"
                desc_box = item.find("div.listing-item__message", first=True)
                if desc_box is not None:
                    item_data["desc"] = desc_box.text
                else:
                    item_data["desc"] = "No description"
                cost_box = item.find("div.listing-item__price", first=True)
                item_data["cost"] = cost_box.text.replace(" ", "").replace(" ", " ")
                loc_box = item.find("div.listing-item__location", first=True)
                item_data["location"] = loc_box.text
                result.append(item_data)
            num += 1


class RabotaBy(Parser):
    # div.vacancy-serp-item-body__main-info > div:nth-child(1) > h3 > span > span > a
    # div.vacancy-serp-item-body__main-info .bloko-link
    # div.vacancy-serp-item-body__main-info div.vacancy-serp-item__meta-info-company > a
    # div.bloko-h-spacing-container.bloko-h-spacing-container_base-0 > div.bloko-text
    # div.vacancy-serp-item-body div:nth-child(1) > span
    ITEMS_ROOT = "#a11y-main-content"

    def _parse(self):
        num = 0
        result = []
        while True:
            page = self._get_page(num)
            items_box = page.html.find(self.ITEMS_ROOT, first=True)
            items = items_box.find("div.serp-item")
            if items == []:
                return result
            for item in items:
                item_data = {}
                url_box = item.find("div.vacancy-serp-item-body__main-info .bloko-link", first=True)
                item_data["url"] = url_box.attrs["href"]
                company_box = item.find("div.vacancy-serp-item__meta-info-company > a", first=True)
                item_data["company"] = company_box.text.replace(" ", " ")
                country_box = item.find("div.vacancy-serp-item__info > div.bloko-text", first=True)
                item_data["country"] = country_box.text
                experience_box = item.find("div.bloko-h-spacing-container.bloko-h-spacing-container_base-0 > "
                                           "div.bloko-text", first=True)
                item_data["experience"] = experience_box.text
                salary_box = item.find("div.vacancy-serp-item-body div:nth-child(1) > span", first=True)
                if salary_box is None:
                    item_data["salary"] = "Unknown"
                else:
                    item_data["salary"] = salary_box.text.replace(" ", "")
                result.append(item_data)
            num += 1


if __name__ == "__main__":
    # https://cars.av.by/filter?brands[0][brand] = 8 & page = 2
    av = AvBy("https://cars.av.by/filter", params={"brands[0][brand]": "5782"})
    av.start()
    av.save()

    # https://rabota.by/vacancies/programmist?page = 0
    rb = RabotaBy("https://rabota.by/vacancies/arkhitektor", params={})
    rb.start()
    rb.save()
