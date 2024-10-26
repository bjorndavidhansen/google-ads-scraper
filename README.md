# google-ads-scraper
A web scraping tool that automates Google Ads extraction using Selenium and undetected_chromedriver. It searches ads based on keywords and locations, collects ad info, and extracts phone numbers, logging results as CSV files.
# Objective
    The purpose of this GoogleAdsScraper project is to automate the process of 
    collecting data from Google search results for specific keywords and locations. 
    It aims to identify ads in search results, extract information such as website 
    URLs and phone numbers, and store the data in a structured CSV file. The scraper 
    utilizes undetected Chrome WebDriver to bypass bot detection, employs various 
    techniques like randomization in scrolling and delays, and handles errors to 
    maintain stability and consistency in data collection.

# Usage
Update the keywords and locations lists in the main() function with your search terms.
Run the scraper:
bash
Copy code
python google_ads_scraper.py
The scraped data will be saved in a timestamped CSV file in the project directory.
# Dependencies
+ undetected_chromedriver
+ Selenium
+ Pandas
+ fake_useragent
# Project Structure
google_ads_scraper.py: Main script containing the scraper class and functions.
logs/: Folder to store timestamped logs of each scraping session.
results/: Folder to save the output CSV files.
# Image
![IMG_20241026_060902_138](https://github.com/user-attachments/assets/84d1c253-7ab0-42fb-9f2a-5abba6f96021)
