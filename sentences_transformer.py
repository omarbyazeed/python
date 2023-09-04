import numpy as np
import psycopg2
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import os

model = SentenceTransformer('all-MiniLM-L6-v2')
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="admin")
cur = conn.cursor()


def red_cut_insert(path, w):
    with open(path, 'r') as f:
        contents = f.read()
    import textwrap
    s = textwrap.wrap(contents, width=w)
    file_name = os.path.basename(path)
    file_size = os.path.getsize(path)

    cur.execute(" CREATE TABLE IF NOT EXISTS TESTS( id SERIAL PRIMARY KEY ,"
                "text TEXT,embedding BYTEA , filename TEXT, filesize INTEGER )")
    conn.commit()

    for i in s:
        em = model.encode([i])
        embtoby = em.tobytes()
        cur.execute("INSERT INTO TESTS (text, embedding, filename, filesize)"
                    " VALUES (%s, %s ,%s ,%s )", (i, embtoby, file_name, file_size))
        conn.commit()
    print("---DONE---")


def split_text_and_save_to_database(path):

    with open(path, 'r') as f:
        text = f.read()

    sentences = text.split('.')
    file_name = os.path.basename(path)
    file_size = os.path.getsize(path)

    for i in sentences:
        em = model.encode([i])

        embtoby = em.tobytes()

        cur.execute("INSERT INTO TESTS (text, embedding, filename, filesize)"
                    " VALUES (%s, %s ,%s ,%s )",

                    (i, embtoby, file_name, file_size))
        conn.commit()
    print("---DONE---")


def search(i):
        cur.execute("SELECT text,embedding FROM TESTS  ")
        conn.commit()
        data = cur.fetchall()
        ii = model.encode([i])
        for row in data[0:]:
            text = row[0]
            np_array = np.frombuffer(row[1], dtype=np.float32)
            sim = cosine_similarity([ii[0]], [np_array])
            if sim[0] > 0.5:
                print('text : ', text, ' | similarity : ', sim, '\n')


def search_by_text(user_input):
    sen = "SELECT text FROM TESTS WHERE text LIKE %s"
    cur.execute(sen, ('%' + user_input + '%',))
    for i in cur.fetchall():
        print('sen is : ', i)


user = ''
while user != 'f' or user != 's' or user != 'y':
    print("------------------------------------------------------")
    print('chose from this function \n'
          '-------------------------------------\n' 
          '1.to enter  file.txt and cut bu length type : f \n'
          '2.to enter  file.txt and auto cut type : x  \n'
          '3.to search type : s \n'
          '4.to search by text : t \n'
          '5.to exit type : y ')
    print("------------------------------------------------------")
    user = str(input("your input is : "))

    if user == 'f':
        path = str(input('enter path of file'))
        path = os.path.normpath(path)
        length = int(input('enter Sentence length '))
        red_cut_insert(path, length)

    elif user == 's':
        i = input('enter text for search ')
        search(i)

    elif user == 'x':
        i = input('enter path ')
        split_text_and_save_to_database(i)

    elif user == 't':
        user_input = input('enter a word')
        search_by_text(user_input)

    elif user == 'x':
        user_input = input('enter a path')
        search_by_text(user_input)

    elif user == 'y':
        break
cur.close()
conn.close()

#C:\Users\Asus\Desktop\HI.txt
