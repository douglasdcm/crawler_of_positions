from subprocess import PIPE, STDOUT, run
from src.helper.commands import initialize_table
from sqlalchemy import text
from tests.settings import DATABASE_STRING
from src.helper.helper import data_pre_processing_portuguese, Connection


def populate_database_with_desired_jobs(positions):
    initialize_table(DATABASE_STRING)
    with Connection.get_database_connection(DATABASE_STRING).connect() as connection:
        for position in positions:
            descrition_processed = data_pre_processing_portuguese(position['description'])
            connection.execute(text(
                f"insert into positions (url, description) values ('{position['url']}', '{descrition_processed}')"))


def exec_command(params, command, domain="python", sudo=False):
    try:
        cmd = []
        if sudo is True:
            cmd.extend(["sudo"])
        cmd.extend([domain, command])
        if isinstance(params, str):
            params = [params]
        cmd.extend(params)
        result = run(
            cmd,
            stdout=PIPE,
            stderr=STDOUT,
            encoding="utf-8")
        result.check_returncode()
        return result.stdout.strip()
    except Exception:
        raise


def populate_database_with_thecnical_jobs():
    description1 = "jira manager senior dashboards carrer"
    description2 = "jira developer python java postgres sql"
    description3 = "jira tester qa pytest postman jmeter"
    description4 = "ux figma design xd"
    positions = [
        {
            "url": "www.position1.com",
            "description": description1
        },
        {
            "url": "www.position2.com",
            "description": description2
        },
        {
            "url": "www.position3.com",
            "description": description3
        },
        {
            "url": "www.very_looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong_url.com",
            "description": description4
        }
    ]
    populate_database_with_desired_jobs(positions)
