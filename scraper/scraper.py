import os
import csv
import math
import time
import signal

from grab import Grab

FILE_NAME = "data/most-wanted.txt"
# QUERY = "?sort=have%2Cdesc&format_exact=Vinyl&ev=em_rs"
# QUERY = "?sort=hot%2Cdesc&format_exact=Vinyl&ev=em_rs"
QUERY = "?sort=want%2Cdesc&format_exact=Vinyl&ev=em_rs"
# TODO: alles mit &country_exact=Germany


def write_to_disk(records):
    with open(FILE_NAME, "a", encoding="utf-8") as f:
        for record in records:
            f.write(
                "{artist}, {record}, {image}\n".format(
                    artist=record[0], record=record[1], image=record[2]
                )
            )


def get_page(page):
    records = []
    time.sleep(1)  # prevent being ratelimited

    g = Grab(timeout=30, connect_timeout=20)
    g.go("https://www.discogs.com/search/" + QUERY + "&page=" + str(page))

    for elem in g.doc.select('//*[@id="search_results"]/div'):

        # some records don't have any images but we still
        # add them so resuming the current download doesn't break
        if "default-image-as-icon" in elem.select("a").attr("class"):
            image = "no-image"
        else:
            image = elem.select("a/span[2]/img").attr("data-src")

        record = elem.select("h4").text()
        artist = elem.select("h5").text()
        records.append([image, record, artist])

    write_to_disk(records)
    print("page " + str(page) + "/" + str(pages) + " complete!")


if __name__ == "__main__":

    if not os.path.exists(FILE_NAME):
        open(FILE_NAME, "a").close()

    pages = 200  # doesn't go past 200 pages

    current_line = sum(1 for line in open(FILE_NAME))
    start_from = math.floor(current_line / 50) + 1

    if start_from != 1:
        print("resuming from page " + str(start_from))

    for page in range(start_from, pages + 1):
        get_page(page)

