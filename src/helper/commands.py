import logging
import nltk

from src.settings import (CAMPOS_DIFINICAO, TABELA, CAMPOS, DB_TYPE)
from src.database.db_factory import DbFactory
from src.crawler.toy import Toy
from src.crawler.factory import Factory
from src.crawler.toy import Toy
from src.database.db_factory import DbFactory
from src.helper.helper import data_pre_processing_portuguese
from src.similarity.similarity import Similarity


nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')


def install(db_name, db_type):
    msg = "Deleting database {}...".format(db_name)
    print(msg)
    logging.info(msg)
    dbf = DbFactory(db_type)
    db = dbf.get_db()
    try:
        db.deleta_banco(db_name)
    except Exception:
        pass
    msg = "Creating database {}...".format(db_name)
    print(msg)
    logging.info(msg)
    db.cria_banco(db_name)
    db.fecha_conexao_existente()

    # Connect to db_name databse
    dbf = DbFactory(db_type)
    db = dbf.get_db(db_name)
    db.cria_tabela(TABELA, CAMPOS_DIFINICAO)
    msg = "Database created."
    print(msg)
    logging.info(msg)
    db.fecha_conexao_existente()
    print("Installation finished")
    return True


def _finish_driver(chrome):
    chrome.quit()
    msg = "Crawler finished."
    print(msg)
    logging.info(msg)


def _run(database, driver, crawlers=None):
    if crawlers is None:
        crawlers = Factory().get_crawlers()
    chrome = driver
    for crawler in crawlers:
        try:
            if crawler["enabled"]:
                url = crawler["url"]
                msg = "Starting crawler for '{}'...".format(url)
                print(msg)
                logging.info(msg)
                driver = chrome.start(url)
                company = crawler["company"]
                company.set_driver(driver)
                company.set_url(url)
                company.run(database)
        except Exception as e:
            msg = "An error occurred during the execution:\n   {}".format(str(e))
            print(msg)
            logging.info(msg)
    _finish_driver(chrome)
    db = database
    positions = len(db.pega_todos_registros(TABELA, CAMPOS, distinct=True))
    msg = "Existem {} vagas cadastradas.".format(positions)
    print(msg)
    logging.info(msg)


def sanity_check(database, driver):
    """Verify the driver is connecting to web sites and if the content of the page is saved in the database
        Args:
            database: a connection object to a real database
            driver: the web driver, like ChromerDriver
    """
    crawlers = [{
                "company": Toy(),
                "url": "http://www.staggeringbeauty.com/",
                "enabled": True
                }]
    _run(database, driver, crawlers)

    msg = "Removendo registros do sanity check."
    logging.info(msg)
    print(msg)
    urls = [
        "http://toy.com/position_1",
        "http://toy.com/position_2",
        "http://toy.com/position_3"
    ]
    db = database
    for url in urls:
        registros = db.pega_registro_por_condicao(TABELA, "url = '{}'".format(url))
        for registro in registros:
            db.deleta_registro(TABELA, registro[0])
    msg = "Registros removidos."
    logging.info(msg)
    print(msg)
    db.fecha_conexao_existente()
    print("Sanity check finished")
    return True

def help_():
    return("""
Commands:
  --initdb          delete the existing database, if any, and install it again
  --sanity-check    check the installtion and clean the database
  --help            open the help documentation
                    """)

def compare(content, db_name, db_type):
    cv = content
    cv = data_pre_processing_portuguese(cv)
    if len(cv) == 0:
        return "Nenhum resultado encontrado."
    dbf = DbFactory(db_type)
    db = dbf.get_db(db_name)
    positions = db.pega_todos_registros(TABELA, CAMPOS)
    db.fecha_conexao_existente()
    s = Similarity()
    result = s.return_similarity_by_cossine(cv, positions)
    table = '<table class="table table-striped" style="width:100%">'
    table += '<tr><th>% Similaridade</th><th>Link da vaga</th></tr>'
    for key, values in result.items():
        table += '<tr>'
        table += f'<td style="width:20%; text-align: center";> {key} </td>'
        table += f'<td style="width:80%"><a href={values[0]}> {values[0]} </a></td>'
        table += '</tr>'
    table += '</table>'
    return table