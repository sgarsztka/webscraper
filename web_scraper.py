import requests
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import string
import re
import argparse
import time
import smtplib
from colorama import Fore, Back, Style,init
import pprint
import csv
import matplotlib.pyplot as plt

d=0
init()
parser = argparse.ArgumentParser(description='Ceneo webscraper')
parser.add_argument('--url', help="dupa")

args = parser.parse_args()
url = ("http://"+args.url)

def main_parser(url):
    try:
        page = requests.get(url,verify=True)
        print("Strona zwraca: " + str(page.status_code) + " \n")
        soup = BeautifulSoup(page.content, 'html.parser')
        #print(soup.prettify())
        ceny = soup.select(".cell-price .value")
        ceny_lista = [pt.get_text() for pt in ceny]
        #ceny_sorted = sorted(ceny_lista)
        print(ceny_lista, " \n")

        return(ceny_lista)
    except BaseException as e:
        print('Wyjatek: {}'.format(error))


def parse_shops(url):
    try:
        page = requests.get(url,verify=True)
        print(Fore.GREEN + "Strona zwraca: " + str(page.status_code) + " \n")
        soup = BeautifulSoup(page.content, 'html.parser')
        #print(soup.prettify())
        listm = soup.findAll('td',{'class':'cell-store-logo'})
        lista_sklepow = []
        for td in listm:
            img = td.find('img')
            if img is not None:
                lista_sklepow.append(img['alt'])
        print( lista_sklepow ,"\n")
        return(lista_sklepow)
    except BaseException as error:
        print('Wyjatek: {}'.format(error))

def parse_name(url):
    try:
        page = requests.get(url,verify=True)
        print(Fore.GREEN + "Strona zwraca: ",page.status_code)
        soup = BeautifulSoup(page.content, 'html.parser')
        nazwa_produktu = soup.find('strong', class_='js_searchInGoogleTooltip')
        nazwa_produktu_text=(nazwa_produktu.get_text())
        print(Fore.YELLOW + nazwa_produktu_text)
        return(nazwa_produktu_text)
    except BaseException as error:
        print('Wyjatek: {}'.format(error))

def sendemail(from_addr, to_addr_list, cc_addr_list,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:465'):
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message

    server_ssl = smtplib.SMTP_SSL(smtpserver)
    server_ssl.ehlo()
    server_ssl.login(login,password)
    problems = server_ssl.sendmail(from_addr, to_addr_list, message)
    server_ssl.close()
    return (problems)


def save_csv(dane,nazwa):
    result=''
    for i in nazwa:
        if i == '/' or i == '"':
                i = 'x'
        result += i
    try:
        with open('{}.csv'.format(result), 'a', newline='') as csvfile:
            writer = csv.writer(csvfile,delimiter=";")
            writer.writerow(dane)
    except BaseException as error:
        print('Wyjatek: {}'.format(error))

def rysuj(ceny,sklepy):
    plt.plot(ceny)
    plt.ylabel(sklepy)
    plt.show()


ceneo = main_parser(url)
ceneo_old = ceneo
while(True):
    d += 1
    print(Fore.CYAN + "Sprawdzenie oferty nr: ", d)
    nazwa = parse_name(url)
    ceneo= main_parser(url)
    lista_sklepow = parse_shops(url)
    dictionary = dict(zip(lista_sklepow,ceneo))
    sorted_by_value = sorted(dictionary.items(), key=lambda kv: kv[1])
    if ceneo != ceneo_old:
        sendemail(from_addr    = '####',
            to_addr_list = ['###'],
            cc_addr_list = [''],
            subject      = 'Powiadomienie o zmianie ceny' + str(nazwa),
            message      = 'Ceny dla produktu: \n' + str(sorted_by_value),
            login        = '######',
            password     = '####')
        ceneo_old = ceneo
        print(Fore.RED + "cena sie zmienila! Wysylam email")
    #print(Fore.GREEN, sorted_by_value)
    pprint.pprint(sorted_by_value)
    save_csv(ceneo, nazwa)
    #rysuj(ceneo,lista_sklepow)
    time.sleep(600)
