import flask
import os
import sqlite3

from flask import jsonify, request

app = flask.Flask(__name__)
DATABASE = 'db.sqlite'
if not os.path.exists(DATABASE):
    print("Creating database.", flush=True)
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    c.execute('CREATE TABLE parking_spots (id, lng, lat, capacity, count)')
    c.execute('INSERT INTO parking_spots VALUES (0, 2, 4, 100, 0)')
    c.execute('INSERT INTO parking_spots VALUES (1, 6, 1, 200, 0)')
    conn.commit()
    conn.close()


@app.route('/api/parking_spots', methods=['GET'])
def list_parking_spots():
    r = []
    d = request.args.to_dict()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    if 'lng' in d and 'lat' in d:
        lng = int(d['lng'])
        lat = int(d['lat'])
        q = 'SELECT * from parking_spots where lng=? and lat=?'
        + ' and count < capacity'
        c.execute(q, (lng, lat))
        conn.commit()
        for i in c.fetchall():
            r.append(jsonify_spot(i))

    elif 'lng' in d and 'lat' not in d:
        lng = int(d['lng'])
        q = 'SELECT * from parking_spots where lng=? and count < capacity'
        c.execute(q, (lng,))
        conn.commit()
        for i in c.fetchall():
            r.append(jsonify_spot(i))

    elif 'lng' not in d and 'lat' in d:
        lat = int(d['lat'])
        q = 'SELECT * from parking_spots where lat=? and count < capacity'
        c.execute(q, (lat,))
        conn.commit()
        for i in c.fetchall():
            r.append(jsonify_spot(i))

    elif 'lng' not in d and 'lat' not in d:
        q = 'SELECT * from parking_spots where count < capacity'
        c.execute(q)
        conn.commit()
        for i in c.fetchall():
            r.append(jsonify_spot(i))

    return jsonify({'available': r})


def jsonify_spot(row):
    content = {
        'id': row[0],
        'lng': row[1],
        'lat': row[2],
        'capacity': row[3],
        'count': row[4]
    }
    return content


@app.route('/api/reservations', methods=['POST'])
def reserve():

    d = request.values.to_dict()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    if 'parking_spot' in d:
        parking_spot = int(d['parking_spot'])
        q = 'UPDATE parking_spots SET count=count+1 WHERE id=?'
        c.execute(q, (parking_spot,))
        conn.commit()

    conn.commit()
    conn.close()
    return jsonify({'reserved': 'success'})


if __name__ == '__main__':
    # python app.py
    app.run(debug=True, host='0.0.0.0', port=8080)
