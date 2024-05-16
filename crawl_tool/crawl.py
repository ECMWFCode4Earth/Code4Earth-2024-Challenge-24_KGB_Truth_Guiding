"""Crawl publications from ECMWF homepage."""

import urllib.request
import os
import time
import re
import click
from bs4 import BeautifulSoup

OUTPUT_ROOT = "/home/user/large-disk/crawled_resources/"
output_subdirectory = {
    'memoranda':"technical_memoranda",
    'ERA':'ERA_Reports',
    'esa-eumetsat': "esa_or_eumetsat_contract_reports",
    'eumetsat-ecmwf':"eumetsat_ecmwf_fellowship_programme_research_reports",
    'report':"reports",
    # 'newsletter':"newsletter"
}

source_url = {
    'memoranda':"https://www.ecmwf.int/en/publications/technical-memoranda",
    'ERA':"https://www.ecmwf.int/en/publications/search?page=0&solrsort=ts_biblio_year%20desc&bib_event_series=%22ERA-40%20Project%20Report%20Series%22%20OR%20%22ERA%20Report%20Series%22",
    'esa-eumetsat':"https://www.ecmwf.int/en/publications/search?searc_all_field=&bib_title=&bib_event_series=%22ESA%20Contract%20Report%22%20OR%20%22EUMETSAT%20Contract%20Report%22&bibcite_year=&bib_issues_number=&name=&f%5B0%5D=sm_biblio_type%3AReport&retain-filters=1&sort=bibcite_year&order=desc",
    'eumetsat-ecmwf':"https://www.ecmwf.int/en/publications/search?solrsort=ts_biblio_year%20desc&f%5B0%5D=sm_biblio_type%3AReport&bib_event_series=%22EUMETSAT/ECMWF%20Fellowship%20Programme%20Research%20Report%22",
    'report':"https://www.ecmwf.int/en/publications/search?sort=bibcite_year&order=desc&f%5B0%5D=filter_by_type_of_publication%3Areport",
    # 'newsletter':"https://www.ecmwf.int/en/publications/newsletters"
}

page_range = {
    'memoranda':38,
    'ERA':4,
    'esa-eumetsat':5,
    'eumetsat-ecmwf':3,
    'report':23,
    # 'newsletter':1
}

page_symbol = {
    'memoranda':'?',
    'ERA':'&',
    'esa-eumetsat':'&',
    'eumetsat-ecmwf':'&',
    'report':'&',
    # 'newsletter':''
}


def generate_link_from_page_number(page_number, source):
    """
    Return memoranda url from page number
    Example: https://www.ecmwf.int/en/publications/technical-memoranda?page=1 from page_number = 2

    Args:
        page_number (int or [a,b])  : Page numbers.
        source (str)                : Source to crawl from.
    """
    url_list = []
    root = source_url[source]
    if re.match(r'^\d+$', page_number): #match an integer
        page_number = int(page_number[0])
        if page_number < 1 or page_number > 38:
            raise ValueError("Page number out of range")
        if page_number == 1:
            url_list.append(root)
        else:
            url_list.append(f"{root}{page_symbol[source]}page={page_number-1}")
    elif re.match(r'^\[\s*[1-9]\d*\s*,\s*[1-9]\d*\s*\]$', page_number): #match form [a,b]
        page_number = page_number.replace(" ","")[1:-1].split(',')
        start = int(page_number[0])
        end = int(page_number[1])
        if start < 1 or end >page_range[source] or start > end:
            raise ValueError("Page number out of range or start > end")
        for page in range(start, end+1):
            if page == 1:
                url_list.append(root)
            else:
                url_list.append(f"{root}{page_symbol[source]}page={page-1}")
    else:
        raise ValueError("Wrong format of page number")
    return url_list

def crawl(url_list, download, wait_time ,verbose, source):
    """
    Crawl all pdf links from page of ECMWF and download.
    
    Args:
        url (str)               : URL of each memoranda page.
        output_address (str)    : Location to store crawled files.
        download (bool)         : Download or not pdf files.
        verbose (bool)          : Print pdf links.
        source (str)            : Source to crawl from.
    """
    output_address = os.path.join(OUTPUT_ROOT, output_subdirectory[source])
    for url in url_list:
        print(f"----------------{url}-----------------")
        with urllib.request.urlopen(url) as page_object:
            content = page_object.read()

        soup = BeautifulSoup(content, 'html.parser')
        links = soup.find_all('a', href=True)
        if download:
            print(f"-------Crawling on url {url}-------\n")
        for link in links:
            current_link = link.get('href')
            if current_link.endswith('pdf'):
                full_link = "https://www.ecmwf.int" + current_link
                file_name = current_link.split("/")[-1]
                if verbose:
                    print(full_link)
                if download:
                    urllib.request.urlretrieve(full_link, os.path.join(output_address, file_name))
                    time.sleep(wait_time)


@click.command()
@click.option('--source', required=True,
              type=click.Choice(['memoranda','report', 'ERA',\
                                  'esa-eumetsat', 'eumetsat-ecmwf'],
                                case_sensitive=False), help="Choice the source to crawl from")
@click.option('--pages', required=True, type=str,
              help='Indicate page numbers to download, should be\
              an integer or in form [first page,last page]')
@click.option('--download', is_flag=True, help="Download or not pdf files")
@click.option('--verbose', is_flag=True, help="Print pdf links")
@click.option('--wait_time', type=float, default=2, help="Wait time between downloads")
def run(**kwargs):
    """Main function"""
    page_number = kwargs['pages']
    download = kwargs['download']
    verbose = kwargs['verbose']
    wait_time = kwargs['wait_time']
    source = kwargs['source']
    print(f"Setting: {kwargs}")
    url_list  = generate_link_from_page_number(page_number, source)
    crawl(url_list, download, wait_time, verbose, source)

if __name__ == "__main__":
    run()
