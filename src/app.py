# Some necessary includes: Flask, SQLite and some system functions
from flask import Flask, g, render_template, redirect, request
import sqlite3 as lite
import sys, os
from subprocess import *
# Tornado web server
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

# Database name. You may use any other database name you like.
DATABASE = '/home/pi/mp3/streams.db'
DATABASE = 'streams.db'

# Just a debugging flag to switch off Flask and Tornado
web = True

# Clever people put the database handling into separate files...
# Anyways, the first function simply creates the SQLite database
# Please change/add the music streams to your liking.
def create_whole_db(DATABASE):
    table_data = {
    'streams':(
    (1,'Lounge FM', r'http://stream.lounge.fm/', 'Lounge', 5),
    (2,'MDR Info',r'http://c22033-ls.i.core.cdn.streamfarm.net/QpZptC4ta9922033/22033mdr/live/app2128740352/w2128904192/live_de_128.mp3', 'Info', 3),
    (3,'Klassik Radio',r'http://edge.live.mp3.mdn.newmedia.nacamar.net/klassikradio128/livestream.mp3', 'Klassik', 2),
    )}
    #connect to database
    db_connection = lite.connect(DATABASE)
    cursor = db_connection.cursor()
    #create table
    cursor.execute("DROP TABLE IF EXISTS Streams")
    cursor.execute("CREATE TABLE Streams" +\
    "(id INT, name VARCHAR(255), link VARCHAR(255), genre VARCHAR(255), rating INT)")
    for data in table_data['streams']:
        qstr = "INSERT INTO Streams " +\
               "(id, name, link, genre, rating) values ('%d', '%s', '%s', '%s', '%d')" %(data[0], data[1], data[2], data[3], data[4])
        print(qstr)
        cursor.execute(qstr)
        #necessary - at least in windows...
        db_connection.commit()
    db_connection.close()

# This function reads out the table streams from the database.
# It returns a list of dictionaries Flask and Jinja can process.
def return_dict(DATABASE):
    db_connection = lite.connect(DATABASE)
    with db_connection:
        cursor = db_connection.cursor()
        data = cursor.execute("SELECT id, name, link, genre, rating FROM Streams")
        rows = data.fetchall()

        #create list of dictionaries
        dict_here = [dict(id=row[0], name=row[1], link=row[2], genre=row[3], rating=row[4]) for row in rows]
        return dict_here

# To execute commands outside of Python
def run_cmd(cmd):
   p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
   output = p.communicate()[0]
   return output

# Initialize Flask.
if web:
    app = Flask(__name__)

if web:
    @app.route('/')
    def show_entries():
        general_Data = {
        'title' : 'Jukebox v0.1'}
        stream_entries = return_dict(DATABASE)
        return render_template('main_bootstrap.html', entries = stream_entries, **general_Data)

    # We do stop the music...
    @app.route('/stop')
    def stop_music():
        run_cmd('mpc stop')
        return redirect('/')

    # Play a stream from the id provided in the html string.
    # We use mpc as actual program to handle the mp3 streams.
    @app.route('/<int:stream_id>')
    def mpc_play(stream_id):
        db_connection = lite.connect(DATABASE)
        with db_connection:
            cursor = db_connection.cursor()
            data = cursor.execute("SELECT link FROM Streams WHERE id='%d'" % (stream_id) )
            link_here = data.fetchone()[0]
            run_cmd('mpc clear')
            run_cmd( ['mpc add %s' % (link_here)])
            print( link_here)
            run_cmd('mpc play')
            return redirect('/')

    # Shutdown the computer.
    @app.route('/shutdown')
    def shutdown_now():
        run_cmd('sudo halt')
        return 'Goodbye'

    # To gracefully shutdown the web application.
    @app.route('/shutdown_server', methods=['POST', 'GET'])
    def shutdown():
        IOLoop.instance().stop()
        return 'Shutting down the server.\nSee you soon :)'

# Here comes the main call.
# See how simple it is to launch a Tornado server with HTTPServer.
if __name__ == "__main__":
    create_whole_db(DATABASE)

    if web:
        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(8080)
        IOLoop.instance().start()