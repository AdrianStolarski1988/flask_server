# from random import choice

# import flask
from flask import request, jsonify, abort, Flask
import sqlite3
from flask_classful import FlaskView, route

app = Flask(__name__)
app.config["DEBUG"] = True
database = "database.db"

quotes = [
    "A noble spirit embiggens the smallest man! ~ Jebediah Springfield",
    "If there is a way to do it better... find it. ~ Thomas Edison",
    "No one knows what he can do till he tries. ~ Publilius Syrus"
]



def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class FlaskView(FlaskView):
    # route_base = "solwit"

    def index(self):
        return "jajaja"
    #
    # def get(self, id):
    #     id = int(id)
    #     if id < len(quotes) - 1:
    #         return quotes[id]
    #     else:
    #         return "Not Found", 404



    @route('/all/', methods = ['GET'])
    def api_all(self):
        with sqlite3.connect(database) as conn:
            conn.row_factory = dict_factory
            cur = conn.cursor()
            results = cur.execute('SELECT * FROM result;').fetchall()
        return jsonify(results)

    @route('/add/', methods=['POST'])
    def api_add(self):
        # query_parameters = request.get_json()
        query_parameters = request.form

        single_line_1 = query_parameters.get('SingleLine1')
        single_line2 = query_parameters.get('SingleLine2')
        email = query_parameters.get('Email')
        phone_number = query_parameters.get('PhoneNumber_countrycode')
        single_line3 = query_parameters.get('SingleLine3')
        decision_box = query_parameters.get('DecisionBox')
        decision_box1 = query_parameters.get('DecisionBox1')

        with sqlite3.connect(database) as conn:
            conn.row_factory = dict_factory
            cur = conn.cursor()

            cur.execute(
                "INSERT INTO result (SingleLine1,SingleLine2,Email,PhoneNumber,SingleLine3,DecisionBox,DecisionBox1 ) "
                "VALUES(?, ?, ?, ?, ?, ?, ?)", (
                    single_line_1, single_line2, email, phone_number, single_line3, decision_box, decision_box1))
            conn.commit()

        results = cur.execute('SELECT * FROM result ORDER BY id DESC Limit 1;').fetchall()
        return jsonify(results), 201

    @route('/records/', methods=['GET'])
    def api_filter(self):
        query_parameters = request.args

        record_id = query_parameters.get('id')
        email = query_parameters.get('Email')
        phone = query_parameters.get('PhoneNumber')

        query = "SELECT * FROM result WHERE"

        if record_id:
            query += f' id="{record_id}" AND'
        if email:
            query += f' email="{email}" AND'
        if phone:
            query += f' PhoneNumber="{phone}" AND'
        if not (record_id or email or phone):
            abort(404)

        query = query[:-4] + ';'

        with sqlite3.connect(database) as conn:
            conn.row_factory = dict_factory
            cur = conn.cursor()

            results = cur.execute(query).fetchall()

        return jsonify(results)

    @route('/delete/<int:record_id>', methods=['DELETE'])
    def api_delete(self, record_id):
        with sqlite3.connect(database) as conn:
            conn.row_factory = dict_factory
            cur = conn.cursor()
            cur.execute(f'DELETE FROM result WHERE id={record_id};')
            conn.commit()

        return "record has been deleted", 202

    @app.errorhandler(404)
    def page_not_found(self):
        return "<h1>404</h1><p>404. Page not found</p>", 404


FlaskView.register(app)

if __name__ == "__main__":
    app.run()