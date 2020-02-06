import logging
from multiprocessing import dummy

import pytest
import requests
from assertpy import assert_that
from assertpy import soft_assertions
from bs4 import BeautifulSoup

from src.main.allure_helpers import arrange, act, assertion


# test goes about 45 seconds
def test_multiprocessor_sitemap_checker():
    sitemap_link: str = "https://bonus.qiwi.com/sitemap"
    link_startswith: str = "https://bonus.qiwi.com"

    with arrange('Get sitemap page source'):
        page_source = requests.get(sitemap_link).text

    with act('Collect all links from sitemap'):
        list_sitemap_links = links_starting_with(page_source, link_startswith)

    with assertion(f'Check all links return code 200, Links count "{len(list_sitemap_links)}"'):
        threads = 15
        with dummy.Pool(processes=threads) as pool:
            with soft_assertions():
                pool.map(assert_status_code_is_200, list_sitemap_links)


# test goes about 9 minutes
@pytest.mark.skip(reason='gitlab execution time economy')
def test_one_thread_sitemap_checker():
    sitemap_link = "https://bonus.qiwi.com/sitemap"
    link_startswith = "https://bonus.qiwi.com"

    with arrange('Get sitemap page source'):
        page_source = requests.get(url=sitemap_link).text

    with act('Collect all links from sitemap'):
        list_sitemap_links = links_starting_with(page_source, link_startswith)

    with assertion('Check all links return code 200'):
        for link in list_sitemap_links:
            with soft_assertions():
                assert_status_code_is_200(link)


def links_starting_with(page_source, schema):
    # load page source in parse able way
    soup = BeautifulSoup(page_source, 'html.parser')
    # collect all links from "href" attribute on the page into links_list
    links_list = [link.get('href') for link in soup.find_all('a')]
    # filter all links with by starts with schema
    filtered_links_list = list(filter(lambda lnk: lnk.startswith(schema), links_list))
    # return filtered links list
    return filtered_links_list


def assert_status_code_is_200(link):
    code = requests.get(url=link).status_code
    logging.info(f'{code} {link}')
    assert_that(val=code, description='status code for link "' + link + '"').is_equal_to(200)
