import config
import pymysql


def create_table_agents():
    con = pymysql.connect(host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
    cur = con.cursor()   

    cur.execute("CREATE TABLE IF NOT EXISTS agents(id INT NOT NULL AUTO_INCREMENT, `agent_id` VARCHAR(20), PRIMARY KEY (id))")
    cur.execute(f"ALTER TABLE agents CONVERT TO CHARACTER SET utf8mb4")

    cur.close()
    con.close()

def create_table_categories():
    con = pymysql.connect(host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
    cur = con.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS categories(id INT NOT NULL AUTO_INCREMENT, name VARCHAR(255), PRIMARY KEY (id))")
    cur.execute(f"ALTER TABLE categories CONVERT TO CHARACTER SET utf8mb4")

    cur.close()
    con.close()


def create_table_market():
    con = pymysql.connect(host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
    cur = con.cursor()
    
    cur.execute("CREATE TABLE IF NOT EXISTS market(id INT NOT NULL AUTO_INCREMENT, name_tovar VARCHAR(255), price DECIMAL(10, 2), kolvo INT, `file_id` VARCHAR(250), `file_name` VARCHAR(2048), `type` VARCHAR(20), `opisanie` VARCHAR(250), `photo` VARCHAR(250), category_id INT, PRIMARY KEY (id), FOREIGN KEY (category_id) REFERENCES categories(id))")
    cur.execute(f"ALTER TABLE market CONVERT TO CHARACTER SET utf8mb4")

    cur.close()
    con.close()


def create_table_passwords():
    con = pymysql.connect(host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
    cur = con.cursor()   

    cur.execute("CREATE TABLE IF NOT EXISTS passwords(id INT NOT NULL AUTO_INCREMENT, `password` VARCHAR(20), PRIMARY KEY (id))")
    cur.execute(f"ALTER TABLE passwords CONVERT TO CHARACTER SET utf8mb4")

    cur.close()
    con.close()


def create_table_files():
    con = pymysql.connect(host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
    cur = con.cursor()   

    cur.execute("CREATE TABLE IF NOT EXISTS files(id INT NOT NULL AUTO_INCREMENT, `req_id` VARCHAR(20), `file_id` VARCHAR(250), `file_name` VARCHAR(2048), `type` VARCHAR(20), PRIMARY KEY (id))")
    cur.execute(f"ALTER TABLE files CONVERT TO CHARACTER SET utf8mb4")

    cur.close()
    con.close()


def create_table_requests():
    con = pymysql.connect(host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
    cur = con.cursor()   

    cur.execute("CREATE TABLE IF NOT EXISTS requests(req_id INT NOT NULL AUTO_INCREMENT, `user_id` VARCHAR(20), `req_status` VARCHAR(20), PRIMARY KEY (req_id))")
    cur.execute(f"ALTER TABLE requests CONVERT TO CHARACTER SET utf8mb4")

    cur.close()
    con.close()


def create_table_messages():
    con = pymysql.connect(host=config.MySQL[0], user=config.MySQL[1], passwd=config.MySQL[2], db=config.MySQL[3])
    cur = con.cursor()   

    cur.execute("CREATE TABLE IF NOT EXISTS messages(id INT NOT NULL AUTO_INCREMENT, `req_id` VARCHAR(20), `message` VARCHAR(4096), `user_status` VARCHAR(20), `date` VARCHAR(50), PRIMARY KEY (id))")
    cur.execute(f"ALTER TABLE messages CONVERT TO CHARACTER SET utf8mb4")

    cur.close()
    con.close()



create_table_agents()
create_table_passwords()
create_table_files()
create_table_categories()
create_table_market()
create_table_requests()
create_table_messages()
print("База данных успешно создана")
