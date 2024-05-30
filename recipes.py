import sqlite3
import time
from bs4 import BeautifulSoup
import requests

# Database setup
conn = sqlite3.connect('recipes.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS recipes (title TEXT, ingredients TEXT, rating REAL)''')

# Function to scrape data from a given URL
def scrape_recipe(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the recipe title
    title = soup.find('h1', class_='headline heading-content').text.strip()

    # Extract the ingredients
    ingredients_list = soup.find_all('span', class_='ingredients-item-name')
    ingredients = [ingredient.text.strip() for ingredient in ingredients_list]
    ingredients_str = ', '.join(ingredients)

    # Extract the rating
    rating_element = soup.find('span', class_='review-star-text')
    rating = None
    if rating_element:
        rating_text = rating_element.text.strip()
        rating = float(rating_text.split()[1])  # Assuming the format is "Rating: X.Y stars"

    return title, ingredients_str, rating

# Main function to scrape the main page and individual recipe pages
def main():
    main_url = 'https://www.allrecipes.com/recipes/'
    response = requests.get(main_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all the recipe links (modify the selector as per your requirement)
    links = soup.find_all('a', href=True)

    # Extract the href attributes to get the URLs
    urls = [link['href'] for link in links if '/recipe/' in link['href']]

    # Iterate over the URLs and scrape data
    for url in urls:
        try:
            title, ingredients, rating = scrape_recipe(url)
            print(f'Scraped {title}')

            # Insert the data into the database
            c.execute('INSERT INTO recipes (title, ingredients, rating) VALUES (?, ?, ?)',
                      (title, ingredients, rating))
            conn.commit()
        except Exception as e:
            print(f'Failed to scrape {url}: {e}')


def scrape_repeatedly(interval_minutes):
    while True:
        main()
        print(f"Waiting {interval_minutes} minutes...")
        time.sleep(interval_minutes * 60)

if __name__ == '__main__':
    try:
        scrape_repeatedly(10)
    except KeyboardInterrupt:
        print("Scraping stopped by user.")
    finally:
        conn.close()
        print('DONE!')
