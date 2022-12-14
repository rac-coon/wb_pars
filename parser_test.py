import requests

def check(id):
    resp = requests.get("https://card.wb.ru/cards/detail?nm=" + str(id)).json()
    name = ''
    price = 0.0
    for item in resp['data']['products']:
        name = item['name']
        price = item['salePriceU']
    return price/100, name

def pars_articles(id_articles):
    pars_result = {}
    for article in id_articles:
        result = check(article)
        articles_dict = {}
        # добавляем в словарь по артикулу словарь с именем result[1] и ценой result[1] из check()
        articles_dict[result[1]] = result[0]
        pars_result[article] = articles_dict
    return pars_result

if __name__ == '__main__':
    # articles = [123214, 412412, 4124125, 1245235, 654224, 9724892]
    # print(check_list(articles))
    print(check(20873873))
    pass
