import sqlite3
import tempfile
import shutil
import configparser
import os

class FirefoxHistory():
    def __init__(self):
        #   Results number
        self.limit = None

        #   Set history location
        history_location = self.searchPlaces()

        #   Temporary  file
        #   Using FF63 the DB was locked for exclusive use of FF
        #   TODO:   Regular updates of the temporary file
        temporary_history_location = tempfile.mktemp()
        shutil.copyfile(history_location, temporary_history_location)
        #   Open Firefox history database
        self.conn = sqlite3.connect(temporary_history_location)
        #   External functions
        self.conn.create_function('hostname',1,self.__getHostname)

    def searchPlaces(self):
        #   Firefox folder path
        #firefox_path = os.path.join(os.environ['HOME'], '.mozilla/firefox/')
        #   snap
        firefox_path = os.path.join(os.environ['HOME'], 'snap/firefox/common/.mozilla/firefox/')
        #   Firefox profiles configuration file path
        conf_path = os.path.join(firefox_path,'profiles.ini')
        #   Profile config parse
        profile = configparser.RawConfigParser()
        profile.read(conf_path)
        prof_path = profile.get("Profile0", "Path")
        #   Sqlite db directory path
        sql_path = os.path.join(firefox_path,prof_path)
        #   Sqlite db path
        return os.path.join(sql_path,'places.sqlite')

    #   Get hostname from url
    def __getHostname(self,str):
        url = str.split('/')
        if len(url)>2:
            return url[2]
        else:
            return 'Unknown'

    def search(self, term):
        query = 'SELECT A.title, url FROM moz_bookmarks AS A'
        query += ' JOIN moz_places AS B ON(A.fk = B.id)'
        query += ' WHERE A.title LIKE "%%%s%%"' % term

        if term == "":
            query += ' ORDER BY A.lastModified DESC'
        else:
            query += ' ORDER BY instr(LOWER(A.title), LOWER("%s")) ASC' % term
        query += ' LIMIT %d' % self.limit


        #   Query execution
        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows

    def close(self):
        self.conn.close()
