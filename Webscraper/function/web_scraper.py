import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        headline = soup.find('h1')  # Assuming the headline is in the <title> tag
        words_count = len(headline.get_text().split())
        if words_count == 1:
            n = soup.find_all('span', attrs={
            'class': 'container__headline-text',
            'data-editable': 'headline'
            })
            print(f"This is {headline.get_text(strip=True)} page")
            print(f"There are {len(n)} articles on this page")

        else:
            catagory = soup.find('meta', attrs={'name': 'categormeta-section'})
            print(f"{catagory.get('content')}, Headline: {headline.get_text(strip=True)}")
            post_time = soup.find('meta', attrs={'property': 'article:published_time'})
            update_time = soup.find('meta', attrs={'property': 'article:modified_time'})
            if post_time:
                print(f"Post Time: {post_time.get('content', 'No content attribute found')}")
            if update_time:
                print(f"Update Time: {update_time.get('content', 'No content attribute found')}")

        return response.text
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None