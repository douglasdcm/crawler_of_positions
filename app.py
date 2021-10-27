#!flask/bin/python
import os
import sys
import logging
from src.database.db_factory import DbFactory
from src.settings import CAMPOS_DIFINICAO, DB_NAME, ROOT_DIR, TABELA, CAMPOS, LOGS_FILE
from flask import Flask, render_template, request
from src.similarity.similarity import Similarity
from src.settings import ROOT_DIR, TABELA, CAMPOS
from src.driver.chrome import ChromeDriver
from src.similarity.similarity import Similarity
from src.crawler.factory import Factory
from src.helper.helper import data_pre_processing_portuguese
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    filename=LOGS_FILE, level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

app = Flask(__name__)
sys.path.append(ROOT_DIR)


@app.route('/')
def output():
    # serve index template
    return render_template('index.html')


@app.route('/receiver', methods=['POST'])
def worker():
    limit = 5000
    message = request.json['message']
    message = (message[:limit]) if len(message) > limit else message
    return _compare(message)


@app.route('/update', methods=['POST'])
def update():
    """
    Run the crawlers and update the database with the positons information.
    Request example:
        curl -XPOST -H "Content-type: application/json" -d '{"hash": "dev"}' 'localhost:5000/update'
    """
    data = request.json
    if os.getenv('HASH') == "":
        os.environ['HASH'] = "dev"
    if data["hash"] == os.getenv('HASH'):
        return _update()
    else:
        return "NO ACTION\n"


@app.route('/info', methods=['POST'])
def info():
    """
    Get information of the database, for example, number of rows.
    Request example:
        curl -XPOST -H "Content-type: application/json" -d '{"hash": "dev"}' 'localhost:5000/info'
    """
    data = request.json
    if os.getenv('HASH') == "":
        os.environ['HASH'] = "dev"
    if data["hash"] == os.getenv('HASH'):
        return _info()
    else:
        return "NO ACTION\n"


def _compare(content):
    cv = content
    cv = data_pre_processing_portuguese(cv)
    if len(cv) == 0:
        return "Nenhum resultado encontrado."
    dbf = DbFactory()
    conn = dbf.create_connnection(database=DB_NAME)
    db = dbf.make_db(conn)
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


def _update():
    try:
        _clear()
        _run()
        return "OK\n"
    except Exception as e:
        return "FAIL: \n{}".format(str(e))


def _run(crawlers=None):
    if crawlers is None:
        crawlers = Factory().get_crawlers()
    for crawler in crawlers:
        try:
            chrome = ChromeDriver()
            if crawler["enabled"]:
                url = crawler["url"]
                msg = "Starting crawler for '{}'...".format(url)
                print(msg)
                logging.info(msg)
                driver = chrome.start(url)
                company = crawler["company"]
                company.set_driver(driver)
                company.set_url(url)
                company.run()
            _finish_driver(chrome)
        except Exception as e:
            msg = "An error occurred during the execution:\n   {}".format(str(e))
            print(msg)
            logging.info(msg)


def _clear():
    msg = "Cleaning database..."
    print(msg)
    logging.info(msg)
    dbf = DbFactory()
    conn = dbf.create_connnection(database=DB_NAME)
    db = dbf.make_db(conn)
    try:
        db.deleta_tabela(TABELA)
    except Exception:
        pass
    db.cria_tabela(TABELA, CAMPOS_DIFINICAO)
    msg = "Database created."
    print(msg)
    logging.info(msg)
    db.fecha_conexao_existente()


def _finish_driver(chrome):
    chrome.quit()
    msg = "Crawler finished."
    print(msg)
    logging.info(msg)


def _info():
    dbf = DbFactory()
    conn = dbf.create_connnection(database=DB_NAME)
    db = dbf.make_db(conn)
    max_id = db.pega_maior_id(TABELA)[0][0]
    db.fecha_conexao_existente()
    return "Number of records in database is {}\n".format(str(max_id))


if __name__ == '__main__':
    # run!
    from waitress import serve
    port = int(os.environ.get('PORT', 5000))
    serve(app, host="0.0.0.0", port=port)
    # app.run(host='0.0.0.0', threaded=True, port=port)
