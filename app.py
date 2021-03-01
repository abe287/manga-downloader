import requests
from bs4 import BeautifulSoup
import argparse
import time
import os

class readm():
    #Get the links to the chapters of the manga
    def getChapters(link, website):
        #Get soup of manga page
        src = requests.get(link)
        soup = BeautifulSoup(src.content, 'lxml')

        #Extract links to individual chapters
        chapters = []
        chapter_containers = soup.find_all("div", attrs={"class":"item season_start"})
        for chapter_container in chapter_containers:
            chapters.append("https://readm.org" + chapter_container.find("td", attrs={"class":"table-episodes-title"}).find("a")['href'])
        
        #Remove duplicates (website has some chapters listed twice) and reverse list
        chapters = list(dict.fromkeys(chapters))[::-1]

        return chapters
    
    #Get the title of the chapter and list of images
    def getChapterDetails(chapter):
        src = requests.get(chapter)
        soup = BeautifulSoup(src.content, 'lxml')

        title = soup.find("span", attrs={"class":"light-title"}).text

        image_container = soup.find("div", attrs={"class":"ch-images ch-image-container"}).find("center")
        image_links = image_container.find_all("img")
        image_links = ["https://readm.org/"+x['src'] for x in image_links]

        chapter_details = {"image_links":image_links, "title":title}
        return chapter_details
    
    #Function to download an image to folder
    def downloadImage(image, title, output, i):
        image = requests.get(image)
        if image.status_code == 200:
            os.makedirs(f'{output}/{title}', exist_ok = True)
            open(f"{output}/{title}/{i+1}.jpg", 'wb').write(image.content)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--website", help = "Website name", required = True)
    parser.add_argument("-l", "--link", help = "Link to manga page", required = True)
    parser.add_argument("-o", "--output", help = "Output folder name", required = True)

    args = parser.parse_args()
    link = args.link
    website = args.website
    output = args.output

    if website.lower() == "readm":
        #Get all the chapters from the webpage
        chapters = readm.getChapters(link, website)

        for chapter in chapters:
            #Get the chapter details (chapter title and list of image links)
            chapter_details = readm.getChapterDetails(chapter)
            title, image_links = chapter_details['title'], chapter_details['image_links']

            #Download the images of each chapter to its own folder
            for i, image in enumerate(image_links):
                readm.downloadImage(image, title, output, i)
                #Logs progress to terminal
                end = "\r" if i+1 != len(image_links) else "\n"
                print(f"Downloading {title} | PROGRESS {i+1}/{len(image_links)}", end=end, flush=True)
            
            time.sleep(1)

main()