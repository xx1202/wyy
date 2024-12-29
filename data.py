import pymysql
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Comments:
    def __init__(self):
        try:
            self.conn = pymysql.connect(host='localhost', user='root', password='3445937904px', db="python")
            self.cursor = self.conn.cursor()
        except Exception as e:
            logging.error(f"Error connecting to the database: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """关闭数据库连接和游标"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute_query(self, sql, params=None):
        """执行数据库查询"""
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            return self.cursor.fetchall()
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            self.conn.rollback()
            return None

    def execute_update(self, sql, params=None):
        """执行数据库更新操作"""
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            logging.error(f"Error executing update: {e}")
            self.conn.rollback()
            return 0

    def insert(self, data):
        """插入数据"""
        sql = "INSERT INTO comments (username, content, created_at, likes) VALUES (%s, %s, %s, %s)"
        if not data:
            logging.warning("没有数据")
            return 0
        try:
            self.cursor.executemany(sql, data)
            self.conn.commit()
            logging.info(f"{len(data)}条数据插入成功")
        except Exception as e:
            logging.error(f"Error: {e}")
            self.conn.rollback()
        finally:
            self.close()

    def select(self, num=10):
        """选择数据"""
        sql = "SELECT * FROM comments LIMIT %s;"
        num = int(num) if num else 10
        results = self.execute_query(sql, (num,))
        if results is None:
            logging.warning("查询失败")
            return []
        rows = [{"id": row[0], "username": row[1], "content": row[2], "time": row[3], "likes": row[4]} for row in results]
        return rows

    def delete(self, id):
        """删除数据"""
        sql = "DELETE FROM comments WHERE id = %s"
        if not id:
            return "删除失败：没有提供有效的 ID"
        rowcount = self.execute_update(sql, (int(id),))
        if rowcount > 0:
            return f"删除成功：已删除 id 为 {id} 的记录"
        else:
            return f"删除失败：未能删除 id 为 {id} 的记录"

    def update(self, data: dict, id):
        """更新数据"""
        if not data:
            return "没有需要更新的字段"
        if not id:
            return "没有提供有效的 ID"

        set_clause = []
        values = []
        for key, value in data.items():
            if value is not None:
                set_clause.append(f"{key} = %s")
                values.append(value)

        if not set_clause:
            return "没有有效更新的字段"

        sql = f"UPDATE comments SET {', '.join(set_clause)} WHERE id = %s;"
        values.append(id)
        rowcount = self.execute_update(sql, tuple(values))
        if rowcount > 0:
            return "更新成功"
        else:
            return "更新失败"


if __name__ == '__main__':
    with Comments() as comments:
        print(comments.delete(30))