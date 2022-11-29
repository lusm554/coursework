from bs4 import BeautifulSoup

with open("doc.html") as fp:
    soup = BeautifulSoup(fp, "html.parser")
    print(soup.head.title)

