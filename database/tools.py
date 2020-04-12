import sqlite3
import pandas as pd


class Database:

    def __init__(self, name):
        try:
            self.db_name = name
            self.cn = sqlite3.connect(f'database/{self.db_name}.db')
            self.cur = self.cn.cursor()
        except sqlite3.Error as e:
            raise Exception(f'Failed to connect to database {self.db_name}:\n{e}')

    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_val, exc_tb):
        self.cur.close()
        if isinstance(exc_val, Exception):
            self.cn.rollback()
        else:
            self.cn.commit()
        self.cn.close()

    def close(self):
        if self.cn:
            self.cn.commit()
            self.cur.close()
            self.cn.close()
            print(f'Closed {self.db_name} database connection')

    def create(self, t_name, t_fields, primary_key='id'):
        fields = t_fields.copy()
        fields[primary_key] += ' PRIMARY KEY'
        cmd = f"CREATE TABLE IF NOT EXISTS {t_name}({', '.join([f'{k} {v}' for k, v in fields.items()])})"
        try:
            self.cur.execute(cmd)
            self.cn.commit()
            print(f'Successfully created table - {t_name} (or table was already there)')
        except sqlite3.Error as e:
            print(f'Failed to create table:\n{e}')

    def insert(self, t_name, df):
        records = list(df.itertuples(name=None))
        cmd = f"INSERT INTO {t_name} ({df.index.name}, {', '.join(df.columns)}) VALUES ({', '.join(['?' for i in range(len(df.columns) + 1)])})"
        try:
            self.cur.executemany(cmd, records)
            self.cn.commit()
            print(f'Successfully inserted {len(records)} rows into {t_name}')
        except sqlite3.Error as e:
            print(f'Failed to insert rows in {t_name}:\n{e}')

    def update(self, t_name, df):
        records = list(df.reset_index()[[*df.columns, df.index.name]].itertuples(name=None, index=None))
        cmd = f"UPDATE {t_name} set {', '.join([f'{col} = ?' for col in df.columns])} where {df.index.name} = ?"
        try:
            self.cur.executemany(cmd, records)
            self.cn.commit()
            print(f'Successfully updated {len(records)} rows into {t_name}')
        except sqlite3.Error as e:
            print(f'Failed to update rows in {t_name}:\n{e}')

    def delete(self, t_name, ids, id_key='id'):
        cmd = f"DELETE from {t_name} where {id_key} = ?"
        try:
            self.cur.executemany(cmd, ids)
            self.cn.commit()
            print(f'Successfully deleted {len(ids)} rows from {t_name}')
        except sqlite3.Error as e:
            print(f'Failed to delete rows in {t_name}:\n{e}')

    def select(self, t_name, fields=None, filters=None):
        filter_str = ' where ' + ' AND '.join(
            [f"{k} in ({', '.join(v)})" for k, v in filters.items()]) if filters else ''
        fields_str = ', '.join(fields) if fields else '*'
        cmd = f"SELECT {fields_str} from {t_name}{filter_str}"
        try:
            self.cur.execute(cmd)
            records = self.cur.fetchall()
        except sqlite3.Error as e:
            raise Exception(f'{e}\nFailed to select rows from {t_name}')

        self.cur.execute(f"PRAGMA table_info({t_name})")
        columns_records = self.cur.fetchall()
        id_key = ''.join([x[1] for x in columns_records if x[5] == 1])

        if fields:
            columns = fields
            print(f'Successfully selected {len(records)} rows from {t_name}')
            if id_key in columns:
                return pd.DataFrame(records, columns=columns).set_index(id_key)
            else:
                return pd.DataFrame(records, columns=columns)
        else:
            columns = [x[1] for x in columns_records]
            print(f'Successfully selected {len(records)} rows from {t_name}')
            return pd.DataFrame(records, columns=columns).set_index(id_key)


def handle_db(db_name, queue):
    with Database(db_name) as db:
        while True:
            try:
                func_n, *args = queue.get()
                if func_n == 'close':
                    db.close()
                    break
                func = eval(f'db.{func_n}')
                func(*args)
                queue.task_done()
            except Exception as e:
                print(e)


def str_list(li):
    return [f"'{x}'" for x in li]
