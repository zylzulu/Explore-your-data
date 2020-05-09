import mysql.connector
import sys
import json
import requests
import re
import decimal
from django.core.serializers.json import DjangoJSONEncoder


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

db=sys.argv[1]
node=sys.argv[2]
cnx=mysql.connector.connect(user='inf551',password='inf551',host='localhost',database=db)
cursor = cnx.cursor(buffered=True)

get_tb=(f"use {db}")
show_tb=("show tables")
cursor.execute(get_tb)
cursor.execute(show_tb)
table=[]
for c in cursor:
    table.append(c[0])
index_dic={}
for t in table:
    print(t)
    query=(f"select * from {t}")
    cursor.execute(query)
    s=''
    count=0
    colum_tuple=cursor.column_names
    col=[]
    for c in colum_tuple:
        col.append(c)
    if t=='aliases':
        col[0]='AId'
    elif t=='emailreceivers':
        col[0]='ERId'
    elif t=='emails':
        col[0]='EId'
    primary_key = col[0]
    data=[]
    if db == 'hillary':
        if t == 'emailreceivers':
            t = 'EmailReceivers'
        else:
            t = t.capitalize()
    elif t == 'dept_emp':
        t = 'department_emp'
    elif t == 'dept_manager':
        t = 'department_manag'
    for n in cursor:
        n=dict(zip(col,n))
        data.append(n)
        count+=1
        if count>300 and t=='Emails':
            break
        elif db=='employees' and count>3000:
            break
        else:
            for key,val in n.items():
                try:
                    val = val.split(' ')
                    for v in val:
                        a = ''.join(re.findall('[a-zA-Z]+', v))
                        a = a.lower()
                        dic_temp = {}
                        if a != '':
                            if a not in index_dic:
                                dic_temp['TABLE'] = t
                                dic_temp['COLUMN'] = key
                                dic_temp[primary_key] = n[primary_key]
                                index_dic[a] = []
                                index_dic[a].append(dic_temp)
                            else:
                                dic_temp['TABLE'] = t
                                dic_temp['COLUMN'] = key
                                dic_temp[primary_key] = n[primary_key]
                                index_dic[a].append(dic_temp)
                except AttributeError:
                        pass

    json_d = json.dumps(data, sort_keys=True, indent=4,cls=DjangoJSONEncoder)

    url = f"https://inf551-28882.firebaseio.com/{node}/{t}.json"
    response = requests.put(url, json_d)

json_ind=json.dumps(index_dic, sort_keys=True, indent=4,cls=DecimalEncoder)
url = f"https://inf551-28882.firebaseio.com/{node}/index.json"
response = requests.put(url, json_ind)
