# encoding: utf-8
from httprunner import exception
import MySQLdb
import json, re


class MyDB(object):
    def __init__(self):
        self.conn = MySQLdb.connect(host='10.8.8.217', port=3306, user='root', passwd='123456', db='httprunner',
                                    charset='utf8')
        self.cur = self.conn.cursor()

    def query_schema(self, s_type):
        results = self.query("SELECT s_json FROM httprunner.TestSchema where s_name='{}';".format(s_type))
        self.close()
        try:
            result = results[0][0]
            return result
        except Exception:
            msg = 'the schema "{}" not found'.format(s_type)
            raise exception.SchemaNotFound(msg)

    def update_testcase_request(self, belong_project, t_type, **kwargs):
        if len(kwargs) != 0:
            results = self.query(
                "SELECT * FROM httprunner.TestCaseInfo where belong_project='{}'".format(belong_project))

            u_result = {}
            for result in results:
                u_result[str(result[0])] = json.loads(re.sub('\'', '\"', result[8]))

            for id, t_request in u_result.items():
                if t_type == 'params':
                    if t_type in t_request['test']['request']:
                        for key in kwargs:
                            t_request['test']['request'][t_type][key] = kwargs[key]
                    else:
                        t_request['test']['request'][t_type] = {}
                        for key in kwargs:
                            t_request['test']['request'][t_type][key] = kwargs[key]

                    t_request = json.dumps(t_request, ensure_ascii=False)
                    t_request = re.sub('\"', '\\\'', t_request)
                    sql = "UPDATE httprunner.TestCaseInfo SET `request`='{}' WHERE `id`='{}';".format(t_request, id)
                    self.updateOrdelete(sql)

            self.close()

    def query(self, sql):
        results = None
        try:
            self.cur.execute(sql)
            results = self.cur.fetchall()
        except:
            print("Error: unable to fetch data")

        return results

    def updateOrdelete(self, sql):
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()

    def close(self):
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    my = MyDB()
    print(my.query_schema('devicelist'))
    my.update_testcase_request('151ciimc-fe-api', 'params', token='9*HJkbjlb%^&R567ed%RTJFYKUFRhjk')

