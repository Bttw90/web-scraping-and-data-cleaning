from bs4 import BeautifulSoup
import requests
import pandas as pd

page_url = 'https://www.miaspesa.it/supermercati/esselunga'

source = requests.get(page_url).text
soup = BeautifulSoup(source, 'lxml')

categories_list = []

categories = soup.find('div', class_='widget-container')
links = categories.find_all('a')

for link in links:
    page_url = link['href']
    category_name = link.text.strip()
    categories_list.append((page_url, category_name))

# Popping the last one because it's not needed
categories_list.pop(-1)

csv_created = False

for i in range(len(categories_list)):
    category_url = categories_list[i][0]
    category_source = requests.get(category_url).text
    category_soup = BeautifulSoup(category_source, 'lxml')

    sub_categories_list = []

    sub_categories = category_soup.find('div', class_='widget-container')
    sub_links = sub_categories.find_all('a')

    # Looping through sub-categories per category to get links and names
    for sub_link in sub_links:
        sub_url = sub_link['href']
        sub_category_name = sub_link.text.strip()
        sub_categories_list.append((sub_url, sub_category_name))

    for j in range(len(sub_categories_list)):
        sub_category_url = sub_categories_list[j][0]

        page_index = 1

        while True:

            sub_category_url += '?page=' + str(page_index)
            sub_category_source = requests.get(sub_category_url)

            if sub_category_source.status_code != 200:
                break

            sub_category_soup = BeautifulSoup(sub_category_source.text, 'lxml')

            name_list = []
            full_list = []
            curr_list = []
            quantity_list = []

            products_name = sub_category_soup.find_all('div', class_='title-block-content')
            for name in products_name:
                name = name.a.text.strip()
                name_list.append(name)

            full_prices = sub_category_soup.find_all('div', class_='full-price')
            for price in full_prices:
                price = price.text.strip().split()
                if len(price) != 0:
                    full_list.append(price[0])
                else:
                    full_list.append('')

            curr_prices = sub_category_soup.find_all('div', class_='curr-price')  
            for price in curr_prices:
                price = price.text.strip().split()[0]
                curr_list.append(price)

            quantities = sub_category_soup.find_all('span', class_='size')
            for quantity in quantities:
                quantity = quantity.text.strip().split()
                quantity.pop(0)
                quantity = ' '.join(quantity)
                quantity_list.append(quantity)

            page_index += 1

            data = {'Name': name_list, 'Full Price': full_list, 'Current Price': curr_list, 'Quantity': quantity_list, 'Category': categories_list[i][1], 'Subcategory': sub_categories_list[j][1]}
            df = pd.DataFrame(data)

            if csv_created == False:
                df.to_csv('data.csv', sep=';', mode='a', index=False, header=True)
                csv_created = True
            else:
                df.to_csv('data.csv', sep=';', mode='a', index=False, header=False)

            name_list.clear()
            full_list.clear()
            curr_list.clear()
            quantity_list.clear()

print('OK')