from flask import Flask, request, render_template, jsonify, url_for
from flaskext.mysql import MySQL

app = Flask(__name__)
sql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'ella es una bruja'
app.config['MYSQL_DATABASE_DB'] = 'cherokee'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

sql.init_app(app)
cnx = sql.connect()
cur = cnx.cursor()


@app.route('/')
def index():
    return render_template('search.html')


@app.route('/works')
def works():
    if 'type' in request.args:
        requested_type = request.args['type']
    else:
        requested_type = 'json'

    if requested_type != 'html' and requested_type != 'json':
        return app.make_response(
            (
                f'unsupported request type: "{requested_type}"',
                400,
                {'mimetype': 'application/json'}
            )
        )

    cur.execute('SELECT * FROM work')
    results = cur.fetchall()

    if requested_type == 'json':
        return jsonify(works=results)
    else:
        return render_template('work.html', results=results)


@app.route('/sentences')
def sentences():
    sentence_id = None
    requested_type = None
    english_fragment = None
    cherokee_fragment = None

    if 'id' in request.args:
        sentence_id = request.args['id']

    if 'type' in request.args:
        requested_type = request.args['type']

    if 'en_frag' in request.args:
        english_fragment = request.args['en_frag']

    if 'chr_frag' in request.args:
        cherokee_fragment = request.args['chr_frag']

    # the default request type will be JSON
    if requested_type is None:
        requested_type = 'json'

    # only the HTML and JSON request types are accepeted
    if requested_type != 'html' and requested_type != 'json':
        return app.make_response(
            (
                f'unsupported request type: "{requested_type}"',
                400,
                {'mimetype': 'application/json'}
            )
        )

    # if all non-format arguments were blank, provide general information about valid sentence indices
    if sentence_id is None and english_fragment is None and cherokee_fragment is None:
        cur.execute('SELECT COUNT(*) FROM sentence')
        result = cur.fetchone()

        if requested_type == 'json':
            return jsonify(min_sentence_id=1, max_sentence_id=result[0])
        else:
            return f'the least valid sentence id is 1 and the max is {result[0]}'

    # if there is a sentence id, ignore cherokee and english fragments and just provide that sentence
    if sentence_id is not None:
        cur.execute('''
            SELECT W.name, S.chr, S.eng FROM sentence AS S, work AS W WHERE
            S.sentence_id=%s and S.work_id=W.work_id
        ''', (sentence_id,))
        result = cur.fetchone()

        if result is None:
            return app.make_response(
                (
                    f'invalid sentence id: "{sentence_id}"',
                    400,
                    {'mimetype': 'application/json'}
                )
            )

        if requested_type is 'json':
            return jsonify(work=result[0], cherokee=result[1], english=result[2])
        else:
            return f'{result[2]}: {result[3]}'

    if english_fragment is None:
        english_fragment = ''

    if cherokee_fragment is None:
        cherokee_fragment = ''

    # return sentence ids matching the given cherokee and english fragment information
    cur.execute(
        """
        SELECT sentence_id FROM sentence WHERE 
        chr LIKE %s AND
        eng LIKE %s
        """,
        (f'%{cherokee_fragment}%', f'%{english_fragment}%')
    )
    results = [row[0] for row in cur.fetchall()]

    return jsonify(ids=results)


@app.route('/fillins')
def fillins():
    lvl = None
    fillin_id = None

    if 'lvl' in request.args:
        lvl = request.args['lvl']

    if 'type' not in request.args:
        requested_type = 'json'
    else:
        requested_type = request.args['type']

    if 'id' in request.args:
        fillin_id = request.args['id']

    if fillin_id is not None:
        cur.execute('''
            SELECT S.chr, S.eng, W.word, F.pos, F.lvl FROM sentence AS S, word AS W, fillin AS F WHERE
            F.fillin_id=%s AND F.sentence_id=S.sentence_id AND F.word_id=W.word_id
        ''', (fillin_id,))
        result = cur.fetchone()

        if requested_type == 'json':
            return jsonify(result)
        else:
            return 'aint noin gonna need this'

    if lvl is not None:
        cur.execute('SELECT fillin_id FROM fillin WHERE lvl=%s', (lvl,))
        results = [row[0] for row in cur.fetchall()]

        if requested_type == 'json':
            return jsonify(fillins=results)
        else:
            return 'no can do, for now'
    else:
        result = cur.fetchone()

        if requested_type == 'json':
            return jsonify(min_fillin_id=1, max_fillin_id=result[0])
        else:
            return f'the least allowable fillin id is 1 and the greatest is {result[0]}'
