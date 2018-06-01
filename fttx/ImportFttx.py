# -*- coding:utf-8 -*-
import pymssql



class ImportFttx:
    def __init__(self, tableName, where =''):
        self.host = '192.168.2.21'
        self.user = 'odoo'
        self.pwd = '123456'
        self.db = 'FTTXRUN'
        self.tableName= tableName
        self.where = where
        self.__GetConnect()
        # self.resList = self.ExecNonQuery(tableName)

    def __GetConnect(self):
        if not self.db:
            raise (NameError, "没有设置数据库信息")
        self.conn = pymssql.connect(host=self.host, user=self.user, password=self.pwd, database=self.db, charset="utf8")
        cur = self.conn.cursor()

        if not cur:
            raise (NameError, "连接数据库失败")
        else:
            self.cur = cur

    def ExecQuery(self):
        # cur = self.__GetConnect()
        sql= "select * from " + self.tableName + ' where ' + self.where
        print(sql)
        print(self.cur)
        self.cur.execute(sql)
        resList = self.cur.fetchall()

        getColumnSql =  "select ORDINAL_POSITION,COLUMN_NAME   from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='%s'" % self.tableName
        self.cur.execute(getColumnSql)
        columnList = self.cur.fetchall()

        # 查询完毕后必须关闭连接
        self.conn.close()
        dataDisk= {}
        for res in resList:
            _dataDisk={}
            # for _res in res:
            #     for item in columnList:
            #         _dataDisk[item[1]]=  _res
            n= 0
            while n < len(res):
                _dataDisk[columnList[n][1]]= res[n]
                n = n+1
            dataDisk[res[0]]=_dataDisk
        dataDisk['id']= []
        for rec in resList:
            dataDisk['id'].append(rec[0])
        return dataDisk

    def ExecNonQuery(self, sql):
        cur = self.__GetConnect()
        cur.execute(sql)
        self.conn.commit()
        self.conn.close()


if __name__ == '__main__':
    reslist = ImportFttx('contract_info', 'where id < 10').ExecQuery()
    for k in reslist:
        print(k)
        print(reslist[k])
