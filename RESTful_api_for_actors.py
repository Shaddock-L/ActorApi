import json
import re

import pandas as pd
from flask import Flask
from flask import request
from flask_restx import Resource, Api
from flask_restx import fields
import requests
import datetime
import time
from pandas.io import sql
import sqlite3

import io
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt


app = Flask(__name__)
api = Api(app,
          default="REST API for Actor/Actress",  # Default namespace
          title="z5285799_ass2",  # Documentation Title
          description="This is the assignment2 for comp9321")  # Documentation Description



update_model = api.model("update_data",{
    
    'Identifier' : fields.Integer,
    #'last_update' : fields.String,
    'name' : fields.String,
    'country' : fields.String,
    'gender' : fields.String,
    'birthday' : fields.String,
    'deathday' : fields.String,
    'shows' : fields.List(fields.String)
    })


url_prefix = 'http://api.tvmaze.com/'
url_search_prefix = 'https://api.tvmaze.com/people/'

####################################################################################
#help functions

def get_actors_info(name):
    r = requests.get(url_prefix + "search/people?q=" + name)
    resp = r.json()
    return resp

def get_shows_info(act_id):
    r_crew = requests.get(url_search_prefix + str(act_id) + '/crewcredits?embed=show')
    r_cast = requests.get(url_search_prefix + str(act_id) + '/castcredits?embed=show')
    resp_crew = r_crew.json()
    resp_cast = r_cast.json()
    show_str = ""
    for i in range(len(resp_cast)):
        add_element = resp_cast[i]['_embedded']['show']['name']
        show_str += add_element + " %|% "
    if len(resp_crew) > 1:    
        for j in range(len(resp_crew)):
            add_element = resp_crew[j]['_embedded']['show']['name']
            show_str += add_element + " %|% "
        show_str += resp_crew[-1]['_embedded']['show']['name']
    else:
        for j in range(len(resp_crew)):
            add_element = resp_crew[j]['_embedded']['show']['name']
            show_str += add_element
    return show_str



def what_to_record(person, shows, db_id):
    if not person['country']:
       country = "" 
    else:
        country = person['country']['name']
    if not person['birthday']:
        birthday = ""
    else:
        birthday = person['birthday']
    if not person['deathday']:
        deathday = ""
    else:
        deathday = person['deathday']
    if not person['gender']:
        gender = ""
    else:
        gender = person['gender']

    record = {
              'db_id' : db_id,
              'p_id': person['id'],
              'p_name' : person['name'],
              'country': country,
              'birthday': birthday,
              'deathday': deathday,
              'gender': gender,
              'update_time': (datetime.datetime.fromtimestamp(person['updated'])).strftime("%Y-%m-%d-%H:%M:%S"),
              'show': shows
              }
    return record



def write_in_sql(dataframe, database_file, table_name):
    cnx = sqlite3.connect(database_file)
    sql.to_sql(dataframe, name=table_name, con=cnx, if_exists='append') 

def db_size(database_file, table_name):
    cnx = sqlite3.connect(database_file)
    size = sql.read_sql('select COUNT(*) from ' + table_name, cnx).values.max()
    return size

def read_from_sql(database_file, table_name):
    cnx = sqlite3.connect(database_file)
    return sql.read_sql('select * from ' + table_name, cnx)


def search_by_person_id_in_sql(database_file, table_name, actor_id):
    cnx = sqlite3.connect(database_file)
    sql_query = 'SELECT * FROM ' + table_name + ' WHERE p_id= "' + str(actor_id) + '"'
    return sql.read_sql(sql_query, cnx)

def search_by_db_id_in_sql(database_file, table_name, database_id):
    cnx = sqlite3.connect(database_file)
    sql_query = 'SELECT * FROM ' + table_name + ' WHERE db_id= "' + str(database_id) + '"'
    return sql.read_sql(sql_query, cnx)

def delete_in_sql(database_file, table_name, id):
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    sql_query = 'DELETE FROM ' + table_name + ' WHERE db_id=' + str(id)
    cur.execute(sql_query)
    conn.commit()
    cur.close()
    conn.close()

def update_name_in_sql(database_file, table_name, data, id):
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    sql_query = 'UPDATE ' + table_name + ' SET p_name = ? WHERE db_id = ' + str(id)
    cur.execute(sql_query, [data])
    conn.commit()
    cur.close()
    conn.close()

def update_last_update_in_sql(database_file, table_name, data, id):
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    sql_query = 'UPDATE ' + table_name + ' SET update_time = ? WHERE db_id = ' + str(id)
    cur.execute(sql_query, [data])
    conn.commit()
    cur.close()
    conn.close()

def update_country_in_sql(database_file, table_name, data, id):
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    sql_query = 'UPDATE ' + table_name + ' SET country = ? WHERE db_id = ' + str(id)
    cur.execute(sql_query, [data])
    conn.commit()
    cur.close()
    conn.close()

def update_birthday_in_sql(database_file, table_name, data, id):
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    sql_query = 'UPDATE ' + table_name + ' SET birthday = ? WHERE db_id = ' + str(id)
    cur.execute(sql_query, [data])
    conn.commit()
    cur.close()
    conn.close()

def update_deathday_in_sql(database_file, table_name, data, id):
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    sql_query = 'UPDATE ' + table_name + ' SET deathday = ? WHERE db_id = ' + str(id)
    cur.execute(sql_query, [data])
    conn.commit()
    cur.close()
    conn.close()

def update_gender_in_sql(database_file, table_name, data, id):
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    sql_query = 'UPDATE ' + table_name + ' SET gender = ? WHERE db_id = ' + str(id)
    cur.execute(sql_query, [data])
    conn.commit()
    cur.close()
    conn.close()

def update_show_in_sql(database_file, table_name, data, id):
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    sql_query = 'UPDATE ' + table_name + ' SET show = ? WHERE db_id = ' + str(id)
    cur.execute(sql_query, [data])
    conn.commit()
    cur.close()
    conn.close()

def turn_show_str_to_list(show_s):
    shows = set(show_s.split(' %|% '))
    show_list = []
    for ele in shows:
       if len(ele) != 0:
            show_list.append(ele)
    return show_list

def count_update_number(df):
    cnt = 0
    time_now = datetime.datetime.now().timestamp()
    for t in df['update_time']:
        timeArray = time.strptime(t, "%Y-%m-%d-%H:%M:%S")
        timeStamp_for_last_update = int(time.mktime(timeArray))
        # 24h = 24 * 60 min = 24 * 60 * 60s
        if time_now - timeStamp_for_last_update <= 86400:
            cnt += 1
    return cnt
        
def process_country(df):
    country = df['country']
    c_dict = {}
    for ele in country:
        if ele not in c_dict:
            c_dict[ele] = 1
        else:
            c_dict[ele] += 1
        
    stat = {}
    classification = []
    stat_list = []
    for coun in c_dict:
        stat[coun] = round(100 * (c_dict[coun] / len(country)),1)
        if coun not in classification:
            classification.append(coun)
            stat_list.append(c_dict[coun] / len(country))
    
    return stat, stat_list, classification

def process_gender(df):
    gender = df['gender']
    c_dict = {}
    for ele in gender:
        if ele not in c_dict:
            c_dict[ele] = 1
        else:
            c_dict[ele] += 1
        
    stat = {}
    classification = []
    stat_list = []
    for coun in c_dict:
        stat[coun] = round(100 * (c_dict[coun] / len(gender)),1)
        if coun not in classification:
            classification.append(coun)
            stat_list.append(c_dict[coun] / len(gender))
    
    return stat, stat_list, classification
    

def process_birthday(df):
    b_dict = {}
    birthday = df['birthday']
    birthday = birthday.sort_values(ascending = True)
    for ele in birthday:
        
        if ele not in b_dict:
            b_dict[ele[:4]] = 1
        else:
            b_dict[ele[:4]] += 1

    stat = {}
    classification = []
    stat_list = []
    for b in b_dict:
        stat[b] = round(100 * (b_dict[b] / len(birthday)),1)
        if b not in classification:
            classification.append(b)
            stat_list.append(b_dict[b] / len(birthday))
    
    return stat, stat_list, classification
    

def process_life_status(df):
    d_dict = { 'live' : 0,
               'dead' : 0
        }
    deathday = df['deathday']

    for ele in deathday:
        if ele == '':
            d_dict['live'] += 1
        else:
            d_dict['dead'] += 1
        
    stat = {}
    classification = []
    stat_list = []
    for k in d_dict:
        stat[k] = round(100 * (d_dict[k] / len(deathday)),1)
        if k not in classification:
            classification.append(k)
            stat_list.append(d_dict[k] / len(deathday))
    return stat, stat_list, classification

# plot func, refer from stackflow 
#https://stackoverflow.com/questions/50728328/python-how-to-show-matplotlib-in-flask
def plot_png(label_list, stat_list, title_list):
    fig = plt.figure()
    for i in range(len(label_list)):
        if i == 0:
            ax1 = fig.add_subplot(2,2,1)
            ax1.pie(stat_list[i], labels = label_list[i], autopct='%.1f%%',textprops= {'fontsize':6})
            ax1.set_title(title_list[i], fontsize = 8)
        if i == 1:
            ax2 = fig.add_subplot(2,2,2)
            ax2.pie(stat_list[i], labels = label_list[i], autopct='%.1f%%',textprops= {'fontsize':6})
            ax2.set_title(title_list[i], fontsize = 8)
        if i == 2:
            ax3 = fig.add_subplot(2,2,3)
            ax3.pie(stat_list[i], labels = label_list[i], autopct='%.1f%%',textprops= {'fontsize':6})
            ax3.set_title(title_list[i], fontsize = 8)
        if i == 3:
            ax4 = fig.add_subplot(2,2,4)
            ax4.pie(stat_list[i], labels = label_list[i], autopct='%.1f%%',textprops= {'fontsize':6})
            ax4.set_title(title_list[i], fontsize = 8)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


####################################################################################
# api part 

@api.route("/actors")
class actors(Resource):
     
   #Q1  start#

    query_parser = api.parser()
    query_parser.add_argument('name', required=False, type=str)

    @api.response(201, 'Successful')
    @api.response(400, 'Validation Error')
    @api.response(404, 'Actor does not Exist')
    @api.expect(query_parser, validate=True)
    @api.doc(description="Get an actor")
    def post(self, query_parser=query_parser):
        args = query_parser.parse_args()
        name_init = args['name']
        if name_init is None:
            api.abort(404, "Actor does not Exist")
        #replace all non-English characters
        pattern = '[0-9!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？\"\'！[\\]^_`{|}~]+'
        name = re.sub(pattern, ' ', name_init)
        
        # print('The name is ', name)
        # request to tvmaze and get the actor info and his/her shows info
        resp_json = get_actors_info(str(name))
        
        if len(resp_json) == 0:
            api.abort(404, f"Actor {name} doesn't exist")
            
        # not 100% pattern
        if resp_json[0]['person']['name'].lower() != name.lower():
            api.abort(404, f"Actor {name} doesn't exist")
        
        # make sure the db is not empty
        try:
            size = db_size(database_file, table_name)
        except:
            size = 0
        
        # get the show info and turn the actor & shows info into dataframe format
        show_list = get_shows_info(resp_json[0]['person']['id'])
        record = what_to_record(resp_json[0]['person'], show_list, size)
        df = pd.DataFrame(record, [my_index])
        
        # if the db has not been created
        if size == 0:
            write_in_sql(df, database_file, table_name) 
            df_db = read_from_sql(database_file, table_name)
            return {
                'name' : df_db.iloc[size]['p_name'],
                'id' : int (df_db.iloc[size]['p_id']),
                'last_update' : df_db.iloc[size]['update_time'],
                '_links': {'self' : {
                           'href':
                               f'http://127.0.0.1:{my_port}/actors/{size}'
                            }
                           }
                }, 201
        
        #check whether we imported this actor before
        already_in = search_by_person_id_in_sql(database_file, table_name, resp_json[0]['person']['id'])
        
        if already_in.empty:
            # no, this actor's info is not in db, write in it
            write_in_sql(df, database_file, table_name) 
            df_db = read_from_sql(database_file, table_name)
            db_id = df_db['db_id'][size - 1]
            return {
                'name' : df_db.iloc[size]['p_name'],
                'id' : int (df_db.iloc[size]['p_id']),
                'last_update' : df_db.iloc[size]['update_time'],
               '_links': {
                   'self' : {
                           'href': f'http://127.0.0.1:{my_port}/actors/{db_id + 1}'}
                          }
                }, 201
            
        else:
            # db already has this actor's info
            return {"message": "Actor {} has already been posted".format(resp_json[0]['person']['name'])}, 200
    
  
    #Q1  end#

    
    #Q5 start#
    sort_parser = api.parser()
    sort_parser.add_argument('order_by', required=False, type=str, default = '+id')
    sort_parser.add_argument('page', required=False, type=int, default = 1)
    sort_parser.add_argument('size', required=False, type=int, default = 10)
    sort_parser.add_argument('filter', required=False, type=str, default = 'id,name')
    
    @api.response(201, 'Get available actors Successfully')
    @api.response(400, 'Validation Error')
    @api.response(404, 'Parameter does not exist')
    @api.doc(description="Retrieve the list of available Actors")
    @api.expect(sort_parser, validate=True)
    def get(self, sort_parser = sort_parser):
        # make sure the db is not empty
        try:
            size = db_size(database_file, table_name)
        except:
            size = 0
        if size == 0:
            api.abort(404, f"There is no actor available")
            
        args = sort_parser.parse_args()
        order_by = args['order_by']
        page = args['page']
        size = args['size']
        filter_arg = args['filter']
        
        df = read_from_sql(database_file, table_name)
        col = ['id', 'actor_id', 'name', 'country', 'birthday', 'deathday', 'gender', 'last-update', 'shows']
        
        if size < 1:
            api.abort(404, f"Size {size} is invalid")
        if page < 1 or ( page > 1 and (page - 1) * size + 1 > len(df)):
            api.abort(404, f"Page {page} is invalid")
        
        #sort the df
        order_by = order_by.strip("{} ").split(",")
        order_by = [ele.strip() for ele in order_by]
        #drop the spaces
        order_str = ','.join(order_by)
        order_sign = []
        order_data = []
        
        for ele in order_by:
            if ele[0] == '+':
                order_sign.append(True)
            elif ele[0] == '-':
                order_sign.append(False) 
            else:
                api.abort(404, f"Parameter {ele} is invalid")
            # translate the param to database param
            param = ele[1:]
            if param == 'id':
                order_data.append('db_id')
            elif param == 'name':
                order_data.append('p_name')
            elif param == 'country':
                order_data.append('country')
            elif param == 'birthday':
                order_data.append('birthday')
            elif param == 'deathday':
                order_data.append('deathday')
            elif param == 'last-update':
                order_data.append('update_time')
            else:
                api.abort(404, f"Parameter {ele} is invalid")
            
        ordered_df = df.sort_values(by = order_data, ascending = order_sign)
        
        ordered_df.drop(['index'], axis = 1, inplace = True)
        
        show_list = []
        for show_str in ordered_df['show']:
            show_list.append(turn_show_str_to_list(show_str))
        ordered_df['show_list'] = show_list
        ordered_df.drop(['show'], axis = 1, inplace = True)
        ordered_df.columns = col
        
        start_idx = (page - 1) * size
        end_idx = page * size 
        if end_idx > len(df):
            end_idx = len(df)
        ret = ordered_df.iloc[start_idx : end_idx]
        
        filter_arg = filter_arg.strip("{} ").split(",")
        filter_arg = [ele.strip() for ele in filter_arg]
        #drop the spaces
        filter_str = ','.join(filter_arg)
        
        for key in filter_arg:
            if key not in col:
                api.abort(404, f"Filter parameter {key} is invalid")
        
        ret = ret[filter_arg]
        
        act = ret.to_dict("record")
        
        link = {
                "self": {
                  "href": f"http://127.0.0.1:{my_port}/actors?order={order_str}&page={page}&size={size}&filter={filter_str}"
                }
              }
        
        if page > 1:
            # still have info in following pages
            if end_idx < len(df):
                link = {
                        "self": {
                          "href": f"http://127.0.0.1:{my_port}/actors?order={order_str}&page={page}&size={size}&filter={filter_str}"
                        },
                        "previous": {
                          "href": f"http://127.0.0.1:{my_port}/actors?order={order_str}&page={page-1}&size={size}&filter={filter_str}"
                        },
                        "next": {
                          "href": f"http://127.0.0.1:{my_port}/actors?order={order_str}&page={page+1}&size={size}&filter={filter_str}"
                        }
                      }
            else:
                #next page does not exist
                link = {
                        "self": {
                          "href": f"http://127.0.0.1:{my_port}/actors?order={order_str}&page={page}&size={size}&filter={filter_str}"
                        },
                        "previous": {
                          "href": f"http://127.0.0.1:{my_port}/actors?order={order_str}&page={page-1}&size={size}&filter={filter_str}"
                        }
                      }
        
        else:
            if end_idx < len(df):
                link = {
                        "self": {
                          "href": f"http://127.0.0.1:{my_port}/actors?order={order_str}&page={page}&size={size}&filter={filter_str}"
                        },
                        "next": {
                          "href": f"http://127.0.0.1:{my_port}/actors?order={order_str}&page={page+1}&size={size}&filter={filter_str}"
                        }
                      }
             
        return {'page' : f'{page}',
                'size' : f'{size}',
                'actors' : act,
                '_link' : link
            },201
    
    #Q5 end#
    
    
    
    
    #Q6 start# 
@api.route('/actor/statistics')  
class Act_stat(Resource):
    stat_parser = api.parser()
    stat_parser.add_argument('format', required=True, type=str)
    stat_parser.add_argument('by', required=True, type=str)
    
    @api.response(201, 'Get statistics of the existing actors Successfully')
    @api.response(400, 'Validation Error')
    @api.response(404, 'Actor does not Exist')
    @api.doc(description="Get the statistics of the existing actors")
    @api.expect(stat_parser, validate=True)
    
    def get(self, stat_parser = stat_parser):
        # make sure the db is not empty
        try:
            size = db_size(database_file, table_name)
        except:
            size = 0
        if size == 0:
            api.abort(404, f"There is no actor")
            
        df = read_from_sql(database_file, table_name)
        if len(df) == 0:
            api.abort(404, f"There is no actor")
            
        args = stat_parser.parse_args()
        the_format = args['format']
        #print(the_format)
        if the_format != 'json':
            if the_format != 'image':
                api.abort(404, f"The format parameter {the_format} is invalid, please input 'json' or 'image'")
            
        
        by_what = args['by']
        by_what = by_what.strip("{} ").split(",")
        by_what = [ele.strip() for ele in by_what]
        #drop the spaces
        by_what_str = ','.join(by_what)
        
        #process the data
        total = len(df)
        total_updated = count_update_number(df)
        
        ret = { 'total' : total,
                'total-update' : total_updated
            }
        
        stat_list = []
        label_list = []
        title_list = []
        
        for key in by_what:
            if key == 'country':
                ret[key] = process_country(df)[0]
                stat_list.append(process_country(df)[1])
                label_list.append(process_country(df)[2])
                title_list.append(key)
            elif key == 'gender':
                ret[key] = process_gender(df)[0]
                stat_list.append(process_gender(df)[1])
                label_list.append(process_gender(df)[2])
                title_list.append(key)
            elif key == 'birthday':
                ret[key] = process_birthday(df)[0]
                stat_list.append(process_birthday(df)[1])
                label_list.append(process_birthday(df)[2])
                title_list.append(key)
            elif key == 'life_status':
                ret[key] = process_life_status(df)[0]
                stat_list.append(process_life_status(df)[1])
                label_list.append(process_life_status(df)[2])
                title_list.append(key)
            else:
                api.abort(404, f"The parameter by {key} is invalid")
        
        if the_format == 'json':
            return ret,201
        
        #format is image
        else:
            
            return plot_png(label_list, stat_list, title_list)
        
    #Q6  end#
    
    
    

@api.route('/actor/<int:id>')
@api.param('id', 'The Actor id')
class Act(Resource):  
    
    #Q2  start#
    @api.response(404, 'Actor was not found')
    @api.response(400, 'Validation Error')
    @api.response(200, 'Successful')
    @api.doc(description="Get an Actor by his ID in the database")
    def get(self, id):
        # make sure the db is not empty
        try:
            size = db_size(database_file, table_name)
        except:
            size = 0
        if size == 0:
            api.abort(404, f"Actor with id {id} doesn't exist")
        
        df = read_from_sql(database_file, table_name)
        target = search_by_db_id_in_sql(database_file, table_name, str(id))
        if target.empty:
            api.abort(404, f"Actor with id {id} doesn't exist")
        
        shows = target['show'][0]        
        show_list = turn_show_str_to_list(shows)        
        
        if target['deathday'][0] == '':
            d_day = 'null'
        else:
            d_day = target['deathday'][0]
        
        ret = target.copy()
        ret['deathday'][0] = d_day
        ret['show_l'] = [show_list]
        ret.drop(['index'], axis = 1, inplace = True)
        ret.drop(['show'], axis = 1, inplace = True)
        cur_id = ret['db_id'][0]
        loc = df[df['db_id'] == cur_id].index[0]
        prev_id = -10
        next_id = -10
        if loc > 0:
            prev_id = df.iloc[loc - 1]['db_id']
        if loc < len(df) - 1:
            next_id = df.iloc[loc + 1]['db_id']
            
        if(prev_id > 0 and next_id > 0):     
            link = {
            "self": {
              "href": f"http://127.0.0.1:{my_port}/actors/{cur_id}"
              },
            "previous": {
              "href": f"http://127.0.0.1:{my_port}/actors/{prev_id}"
              },
            "next": {
              "href": f"http://127.0.0.1:{my_port}/actors/{next_id}"
              }
             } 
        elif(prev_id > 0 and next_id < 0):
            link = {
            "self": {
              "href": f"http://127.0.0.1:{my_port}/actors/{cur_id}"
              },
            "previous": {
              "href": f"http://127.0.0.1:{my_port}/actors/{prev_id}"
              }
             }
        else:
            link = {
            "self": {
              "href": f"http://127.0.0.1:{my_port}/actors/{cur_id}"
              },
            "next": {
              "href": f"http://127.0.0.1:{my_port}/actors/{next_id}"
              }
             }
        
        
        ret['_links'] = [link]
        
        return ret.to_dict('records')
        
    #Q2  end#
    
        
    #Q3  start#
    @api.response(404, 'Actor was not found')
    @api.response(400, 'Validation Error')
    @api.response(200, 'Successful')
    @api.doc(description="Delete an actor by his ID")
    def delete(self, id):
        # make sure the db is not empty
        try:
            size = db_size(database_file, table_name)
        except:
            size = 0
        if size == 0:
            api.abort(404, f"Actor with id {id} doesn't exist")
        df = read_from_sql(database_file, table_name)
        target = search_by_db_id_in_sql(database_file, table_name, str(id))
        if target.empty:
            api.abort(404, "Actor with id {} doesn't exist".format(id))
        delete_in_sql(database_file, table_name, id)
        return {"message": f"The actor with id {id} was removed from the database!",
                "id" : id}, 200
    #Q3  end#
    
    
    #Q4  start#
    @api.response(404, 'Actor was not found')
    @api.response(400, 'Validation Error')
    @api.response(200, 'Successful')
    @api.expect(update_model, validate=True)
    @api.doc(description="Update an Actor's infomation by his ID")
    def patch(self, id):
        # make sure the db is not empty
        try:
            size = db_size(database_file, table_name)
        except:
            size = 0
        if size == 0:
            api.abort(404, f"Actor with id {id} doesn't exist")
        
        # make sure id in db
        df = read_from_sql(database_file, table_name)
        target = search_by_db_id_in_sql(database_file, table_name, str(id))
        if target.empty:
            api.abort(404, f"Actor with id {id} doesn't exist")
               
        res = request.json
        update_flag = False
        # actor ID cannot be changed
        if 'Identifier' in res and id != res['Identifier']:
            return {"message": "Identifier cannot be changed".format(id)}, 400
        for key in res:
            if key not in update_model.keys():
                # unexpected column
                return {"message": "Attribute {} is invalid".format(key)}, 400
            if key == 'name': 
                update_name_in_sql(database_file, table_name, res[key], id)
                update_flag = True
            elif key == 'country':
                update_country_in_sql(database_file, table_name, res[key], id)
                update_flag = True
            elif key == 'birthday':
                update_birthday_in_sql(database_file, table_name, res[key], id)
                update_flag = True
            elif key == 'deathday':
                update_deathday_in_sql(database_file, table_name, res[key], id)
                update_flag = True
            elif key == 'gender':
                update_gender_in_sql(database_file, table_name, res[key], id)
                update_flag = True
            elif key == 'shows':
                show_s = ""
                if len(res[key]) == 1:
                    show_s += res[key][0]
                elif len(res[key]) > 1:
                    for i in range(len(res[key]) - 1):
                        show_s += res[key][i] + " %|% "
                    show_s += res[key][-1] 
                update_show_in_sql(database_file, table_name, show_s, id)
                update_flag = True
            
            time_data = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
            if update_flag:
                update_last_update_in_sql(database_file, table_name, time_data, id)
        
       # print (res)
        return {"id": f"{id}",
                "last-update" : time_data,
                "_links": {
                    "self": {
                      "href": f"http://127.0.0.1:{my_port}/actors/{id}"
                     }
                    }
                }, 200
    #Q4  end#
    
    
        
if __name__ == '__main__':
    database_file = 'mydata.db'
    #database_file = 'test.db'
    table_name = 'actors_infomations'
    my_index = 1
    my_port = 5729
    app.run(debug=True, port = my_port)

        
























