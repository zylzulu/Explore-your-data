import pyrebase
from collections import defaultdict
import string
import json
from flask import *
import re
# config = {
#     "apiKey": "AIzaSyApfa9Qw75PM-cLCZnowfdQLdfoH5CG4uI",
#     "authDomain": "world-language-eaf74.firebaseapp.com",
#     "databaseURL": "https://world-language-eaf74.firebaseio.com",
#     "projectId": "world-language-eaf74",
#     "storageBucket": "world-language-eaf74.appspot.com",
#     "messagingSenderId": "911849577123",
# }
config = {
    "apiKey": "AIzaSyBfD1hxaYQW414PstQ5ftapG44nncOzGnE",
    "authDomain": "inf551-28882.firebaseapp.com",
    "databaseURL": "https://inf551-28882.firebaseio.com",
    "projectId": "inf551-28882",
    "storageBucket": "inf551-28882.appspot.com",
    "messagingSenderId": "280076859884",
    "appId": "1:280076859884:web:ed65f090da8bed020ae8c9",
    "measurementId": "G-VFX5L6S6JM"
}


firebase = pyrebase.initialize_app(config)
db = firebase.database()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/process', methods=['POST'])
def process():
    db = request.form['dbb']
    keywords = request.form['kww']
    result = search(db, keywords)
    result = jsonify(result)

    return result
def search(db_name, l):
    global pk_library
    global keywords
    global database_name

    pk_library = dict()
    l = l.lower().split(',')
    keywords = l
    database_name = db_name
    all_kw_result = defaultdict(int)
    all_tuple_contain_kw = defaultdict(set)
    for word in l:
        word=''.join(re.findall('[a-zA-Z]+', word))
        index = db.child(database_name).child('index').child(word).get() #need to add db name
        if not index.val():
            continue
        for i in index.each(): # i : {COL: name, TABLE: city, ID: 3}
            ref = i.val()
            table = ref['TABLE']
            col = ref['COLUMN']
            for key in ref.keys():
                if key != 'TABLE' and key != 'COLUMN':
                    pk_library[table]=key
                    pk = ref[key]
                    break
            all_kw_result[(pk,col,table)] += 1
            all_tuple_contain_kw[(pk,table)].add(word)
    sorted_cell = [(k,v) for k, v in sorted(all_kw_result.items(), key=lambda item: item[1], reverse = True)]
    for key, value in all_tuple_contain_kw.items():
        all_tuple_contain_kw[key] = len(value)
    sorted_tuple = [(k,v) for k, v in sorted(all_tuple_contain_kw.items(), key=lambda item: item[1], reverse = True)]
    return sort_result(sorted_tuple, sorted_cell)

def sort_result(sorted_tuple, sorted_cell):
    if database_name == 'employee':
        sorted_cell = []
    d = defaultdict(list)
    l = len(keywords)
    while l > 0:
        i = 0
        while i < len(sorted_cell):
            if sorted_cell[i][1] == l:
                if sorted_cell[i][0][0] not in d[sorted_cell[i][0][2]]:
                    d[sorted_cell[i][0][2]].append(sorted_cell[i][0][0])
                # print("cell")
                # print(d)
                i += 1
            elif sorted_cell[i][1] > l:
                i += 1
            else:
                break
        j = 0
        while j < len(sorted_tuple):
            if sorted_tuple[j][1] == l:
                if sorted_tuple[j][0][0] not in d[sorted_tuple[j][0][1]]:
                    d[sorted_tuple[j][0][1]].append(sorted_tuple[j][0][0])
                # print("tuple")
                # print(d)
                j += 1
            elif sorted_tuple[j][1] > l:
                j += 1
            else:
                break
        l -= 1
    return look_for_tuple(d)

def look_for_tuple(d):
    primary_key = pk_library
    res_tuple = defaultdict(list)

    for key, value in d.items():
        res_tuple[key] = [0] * len(value)
        print(database_name)
        print(key)
        tup = db.child(database_name).child(key).get()
        for t in tup.each():
            t = t.val()
            col = primary_key[key]
            if col == 'CODE':
                col = 'Code'
            t_val = ''
            for v in t.values():
                t_val += str(v).lower()
            for i in range(len(value)):
                if t[col] == value[i]:
                    for kw in keywords:
                        if kw in t_val: 
                            res_tuple[key][i] = t
    return res_tuple

# @app.route('/navigate/<string:table>/<string:col>/<string:val>')
def navigate(table, col, val):
    # table = request.args.get("tb")
    # col = request.args.get("col")
    # val = request.args.get("val")
    table = table
    if table in ('city','country','countrylanguage'):
        database_name = 'world'
    elif table in ('Persons','Aliases','Emails','EmailReceivers'):
        database_name = 'hillary-clinton-emails'
    else:
        database_name = 'employee'
    col = col
    val = val
    PF_library = {'world':{'ID':[{'city':'ID'}], 'Code':[{'country':'Code'}, {'city':'CountryCode'}, {'countrylanguage':'CountryCode'}], 'language':[{'countrylanguage':'language'}], 'CountryCode':[{'city':'CountryCode'}, {'countrylanguage':'CountryCode'}, {'country':'Code'}]},
                  'employee':{'dep_no':[{'departments':'dep_no'},{'department_emp':'dep_no'},{'department_manag':'dept_no'}],'emp_no':[{'employees':'emp_no'},{'department_emp':'emp_no'},{'department_manag':'emp_no'},{'salaries':'emp_no'},{'titles':'emp_no'}]},
                  'hillary-clinton-emails':{'AId':[{'Aliases':'AId'}],'ERId':[{'EmailReceivers':'ERId'}],'EId':[{'Emails':'EId'}, {'EmailReceivers':'EmailId'}],'Id': [{'Persons':'Id'},{'Aliases':'PersonId'}, {'EmailReceivers':'PersonId'},{'Emails':'SenderPersonId'}],'PersonId':[{'Persons':'Id'},{'Aliases':'PersonId'}, {'EmailReceivers':'PersonId'},{'Emails':'SenderPersonId'}],'EmailId':[{'Emails':'EId'}, {'EmailReceivers':'EmailId'}],'SenderPersonId':[{'Persons':'Id'},{'Aliases':'PersonId'}, {'EmailReceivers':'PersonId'},{'Emails':'SenderPersonId'}]}}
    res = defaultdict(list)
    for i in PF_library[database_name][col]:
        for key, value in i.items():
            nav_table = key
            nav_col = value
        nav_tuple = db.child(database_name).child(nav_table).get() #need to add database
        for t in nav_tuple.each():
            t = t.val()
            # return jsonify(t)
            if str(t.get(nav_col)) != val:
                continue
            else:
                res[nav_table].append(t)
    return res

@app.route('/navi', methods=['POST'])
def navi():
    table = request.form['tb'].strip()
    col = request.form['col'].strip()
    value = request.form['val'].strip()
    print(table, col, value)
    result = navigate(table, col, value)
    return jsonify(result) 

if __name__ == '__main__':
    app.run(debug=True)


