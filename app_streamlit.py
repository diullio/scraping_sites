import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime

def ScrapSCIELO(keyword:str,numberOfNews:int=10):
    link = f'https://search.scielo.org/?q={keyword}&lang=pt&count={numberOfNews}&from=0&output=site&sort=&format=summary&fb=&page=1'

    #Fiz a requisição
    req = requests.get(link)

    #Jogar o HTML Bruto
    soup = BeautifulSoup(req.text, 'html.parser')
    #pego somente o container principal que está o conteudo
    main_container = soup.find('div', attrs={"id":"ResultArea"})
    #pegando os resultados
    results = main_container.find('div',attrs={"class":"results"}).find_all('div', attrs={"class","item"})

    titles = []
    links = []
    #pegando o título e o link dos artigos
    for res in results:
        content = res.find('div',attrs={'class':'col-md-11 col-sm-10 col-xs-11'})
        link = content.find('div',attrs={"class":"line"}).find('a')
        link = link['href'] if link is not None else None
        links.append(link)

        title = content.find('div',attrs={"class":"line"}).find('a').find('strong').text
        titles.append(title)
    
    #pegando datas
    dates = []
    for link in links:
        req = requests.get(link)
        soup = BeautifulSoup(req.text, 'html.parser')
        #print(soup)
        try:
            date_publication = soup.find('ul',attrs={"class":"articleTimeline"}).find('li').text.replace('Publication in this collection',"").strip().replace('\xa0', ' ')
            dates.append(date_publication)
            #dates.append(datetime.strptime(date_publication,'%d %b %Y'))
            
        except AttributeError:
            print(f'Error ao pegar a data do link {link}')
            dates.append(None)
    
    data = {'Title':titles, 'Links':links, 'Publication_Date':dates}

    df = pd.DataFrame(data)
    return df
       
def ScrapPubMed(keyword:str,numberOfNews:int=10):    
    """Variável numberOfNews tem que ser: 10, 20, 50, 100 ou 200.

    Args:
        keyword (str): [description]
        numberOfNews (int, optional): [description]. Defaults to 10.

    Returns:
        [type]: [description]
    """
    link = f'https://pubmed.ncbi.nlm.nih.gov/?term={keyword.lower()}&filter=datesearch.y_5&size={numberOfNews}&sort=date'

    #Fiz a requisição
    req = requests.get(link)

    #Jogar o HTML Bruto
    soup = BeautifulSoup(req.text, 'html.parser')

    soup = soup.find_all('article', attrs={'class':'full-docsum'})

    #Pega a data e link da noticia
    soup = [divs.find('div', attrs={"class":'docsum-wrap'}) for divs in soup]

    noticeName = []
    noticeLink = []
    noticeDataRef = []

    for infos in soup:
        #Pegar link das noticias
        docontent = infos.find('div', class_='docsum-content')
        noticiaCode = docontent.find('a', class_='docsum-title')
        Code = noticiaCode['href'] if noticiaCode else None
        noticiaLink = 'https://pubmed.ncbi.nlm.nih.gov'+Code
        noticeLink.append(noticiaLink)

        #Pegar nome da noticia
        name = noticiaCode.text.strip()
        noticeName.append(name)
        data_ref = docontent.find('div',class_='docsum-citation full-citation').find('span',class_='docsum-journal-citation full-journal-citation').text
        noticeDataRef.append(data_ref)

    df = {'NoticeName':noticeName,'NoticeLink':noticeLink,'DataRef':noticeDataRef}
    df = pd.DataFrame(df)
    df['Date'] = df['DataRef'].apply(lambda x: __GetDataPubMed(x))

    return df
    
def __GetDataPubMed(x):
    date_pattern = r'\b\d{4} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}\b'

    # Extrair as datas usando a expressão regular
    match = re.search(date_pattern, x)
    if match:
        date = match.group()
        date = datetime.strptime(date,"%Y %b %d")

        # Exibir as datas extraídas
        return date

# Configuração inicial da pagina
st.set_page_config(page_title='Web Scrapping', layout='wide')

# Menu de navegação
st.sidebar.header('Navegação')
page = st.sidebar.radio("Selecione uma página", ('PubMed', 'Scielo'))

if page == 'PubMed':
  st.header('Scrapping da Página PubMed')

  with st.form(key='scrapping'):
    keyword = st.text_input('Palavra-Chave')

    submit_button = st.form_submit_button(label='Buscar') 

    if submit_button:
      df = ScrapPubMed(keyword, numberOfNews=20)

      st.header('Consulta do PubMed')   
      st.dataframe(df)

if page == 'Scielo':
  st.header('Scrapping da Página Scielo')

  with st.form(key='scrapping-scielo'):
    keyword = st.text_input('Palavra-Chave')

    submit_button = st.form_submit_button(label='Buscar') 

    if submit_button:
      df = ScrapSCIELO(keyword,numberOfNews=5)

      st.header('Consulta do Scielo')   
      st.dataframe(df)





        



        
    
    


    


      

