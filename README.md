# Multi-Language Wikipedia Article Scraper

This python application finds a wikipedia article for a specified name and language then scrapes the text content of the article, reads it to a text file and downloads the file to the local file location specified by the user. The web scraping is done using the BeatifulSoup library. If the search term used to find an article returns multiple results, the application returns text files of the wikipedia pages for the first five results.

## Running the application

To run the application, open a virtual environment and run pip install requirements.txt to install the python dependencies, then run the command python app.py and the application will run in localhost:5000