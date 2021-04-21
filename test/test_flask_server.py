import sys
import time
import sqlite3
import os
from shutil import copyfile
import pytest
from flask import Flask
from FlaskApp import FlaskView
import csv
from flask import request

timestamp = str(int(time.time()))
insert_into_query = "INSERT INTO result (SingleLine1,SingleLine2,Email,PhoneNumber,SingleLine3,DecisionBox,DecisionBox1 ) VALUES(?, ?, ?, ?, ?, ?, ?)"
post_method = "flask/add/"
get_all_method = "flask/all/"
filter_method = "flask/records"
delete_method = "flask/delete/id"

source_db = "database.db"
target_db = f"test_database{timestamp}.db"
data_to_import = "data_to_import.csv"



dane = {
    "SingleLine1": "imie",
    "SingleLine2": "nazwiosko",
    "SingleLine3": "wiadomosc",
    "Email": f"adrian{timestamp}@solwit.com",
    "PhoneNumber_countrycode": f"{timestamp}",
    "DecisionBox": "on",
    "DecisionBox1": "off",
}


def form_data(**element):
    dane = {
        "SingleLine1": element.get("SingleLine1"),
        "SingleLine2": element.get("SingleLine2"),
        "SingleLine3": element.get("SingleLine3"),
        "Email": element.get("Email"),
        "PhoneNumber_countrycode": element.get("PhoneNumber"),
        "DecisionBox": element.get("DecisionBox"),
        "DecisionBox1": element.get("DecisionBox1"),
    }
    return dane

def copy_files(source, target):
    try:
        copyfile(source, target)
        print("ok")
    except IOError as e:
        print("Unable to copy file. %s" % e)
        exit(1)
    except:
        print("Unexpected error:", sys.exc_info())
        exit(1)

def clear_database(source):
    with sqlite3.connect(source) as conn:
        cur = conn.cursor()
        cur.execute('DELETE FROM result;')
        conn.commit()

def import_data_to_db_from_csv(database_name, data_to_import):
    con = sqlite3.connect(database_name)
    con.execute('CREATE TABLE  IF NOT EXISTS result (id INTEGER PRIMARY KEY AUTOINCREMENT,'
                'SingleLine1 TEXT, '
                'SingleLine2 TEXT, '
                'Email TEXT, '
                'PhoneNumber TEXT,'
                'SingleLine3 TEXT, '
                'DecisionBox TEXT, '
                'DecisionBox1 TEXT'
                ');')
    con.commit()
    con.execute('DELETE FROM result;')
    with open(data_to_import, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")
        for field in csv_reader:
            con.execute(insert_into_query, field)
            con.commit()


copy_files(source_db, target_db)
clear_database(source_db)
import_data_to_db_from_csv(source_db, data_to_import)


app = Flask(__name__)
FlaskView.register(app)
app.config['TESTING'] = True
client = app.test_client()

class TestAPI:
    # def setup_method(self):
        # copy_files(source_db, target_db)
        # import_data_to_db_from_csv(source_db, data_to_import)
        #
        # print("\n dupa")

        # app = Flask(__name__)
        # FlaskView.register(app)
        # app.config['TESTING'] = True
        # client = app.test_client()

        # yield None
        # copy_files(target_db, source_db)
        # os.remove(target_db)


    @pytest.fixture(scope='class')
    def add_record(self):
        post = client.post(post_method, data=dane)
        return post

    def test_status_get_method_should_be_200(self):
        resp = client.get(get_all_method)
        assert resp.status_code == 200

    def test_amount_records_should_be_above_0(self):
        """
        before execute this test data base is imported from csv file
        so GET method should return more than 0 results
        """

        amount_records = len(client.get(get_all_method).json)
        print('\n' + str(amount_records))
        assert amount_records > 0

    def test_not_correct_url_should_return_404(self):
        status = client.get(get_all_method + "sas").status_code
        assert status == 404

    def test_status_post_method_should_be_201(self, add_record):
        assert add_record.status_code == 201

    def test_email_added_should_be_saved(self, add_record):
        assert add_record.json[0]["Email"] == dane["Email"]

    def test_single_line_1_added_should_be_saved(self, add_record):
        assert add_record.json[0]["SingleLine1"] == dane["SingleLine1"]

    def test_single_line_2_added_should_be_saved(self, add_record):
        assert add_record.json[0]["SingleLine2"] == dane["SingleLine2"]

    def test_single_line3_added_should_be_saved(self, add_record):
        assert add_record.json[0]["SingleLine3"] == dane["SingleLine3"]

    def test_decision_box_added_should_be_saved(self, add_record):
        assert add_record.json[0]["DecisionBox"] == dane["DecisionBox"]

    def test_decision_box1_added_should_be_saved(self, add_record):
        assert add_record.json[0]["DecisionBox1"] == dane["DecisionBox1"]

    def test_phone_number_added_should_be_saved(self, add_record):
        assert add_record.json[0]["PhoneNumber"] == dane["PhoneNumber_countrycode"]

    def test_add_record_and_check_email_in_all_result_from_get_method(self):
        data_to_send = form_data(
            SingleLine1="wojtek",
            SingleLine2="wielkopolski",
            SingleLine3="tresc wiadomosci",
            Email=f"xxczxc{timestamp}@solwit.com",
            DecisionBox='OK',
            DecisionBox1="NIE",
            PhoneNumber="000999888")
        # post_method
        client.post(post_method, data=data_to_send)

        # check result
        get_list = client.get(get_all_method).json
        check_if_is_on_list = True if data_to_send.get("Email") in [item['Email'] for item in get_list] else False

        assert check_if_is_on_list

    def test_delete_method_should_remove_record_from_database(self):
        """
            - id check_if_is_on_list = False => record with id was deleted
            - status should return 202
        """

        first_record_id = client.get(get_all_method).json[0]["id"]
        status = client.delete(delete_method.replace("id", str(first_record_id))).status_code
        get_list = client.get(get_all_method).json
        check_if_is_on_list = True if first_record_id in [item['id'] for item in get_list] else False
        print(check_if_is_on_list)

        assert status == 202
        assert not check_if_is_on_list

    def test_get_method_with_filter_by_id(self):
        first_record_id = client.get(get_all_method).json[0]["id"]
        find_records = client.get(filter_method + f"/?id={first_record_id}").json
        assert find_records[0]["id"] == first_record_id
        assert len(find_records) > 0

    def test_get_method_with_filter_by_email(self):
        first_record_with_email = client.get(get_all_method).json[0]["Email"]
        find_records = client.get(filter_method + f'/?Email={first_record_with_email}').json
        assert find_records[0]["Email"] == first_record_with_email
        assert len(find_records) > 0

    def test_filter_method_by_email_should_return_three_elements(self):
        data_to_send = form_data(
            SingleLine1="adam",
            SingleLine2="wielkopolski",
            SingleLine3="tresc wiadomosci",
            Email=f"jajcarz{timestamp}@solwit.com",
            DecisionBox='OK',
            DecisionBox1="NIE",
            PhoneNumber="000999888")
        for i in range(3):
            client.post(post_method, data=data_to_send)

        find_records = client.get(filter_method + f'/?Email=jajcarz{timestamp}@solwit.com').json
        assert len(find_records) == 3

    def test_get_method_with_filter_by_phone_number(self):
        first_record_with_phone_number = client.get(get_all_method).json[0]["PhoneNumber"]
        find_records = client.get(filter_method + f'/?PhoneNumber={first_record_with_phone_number}').json
        assert find_records[0]["PhoneNumber"] == first_record_with_phone_number
        assert len(find_records) > 0

    def test_get_method_with_filter_without_params_should_return_404(self):
        status = client.get(filter_method).status_code
        assert status == 308
