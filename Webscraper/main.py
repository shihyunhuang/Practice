from function.web_scraper import scrape_website

def main():
    input_url = input("Enter the URL to scrape: ")
    if input_url:
        content = scrape_website(input_url)
        
    else:
        print("No URL provided. Exiting.")

if __name__ == "__main__":
    main()
