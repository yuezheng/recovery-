
import MySQLdb

class mysqlOperater：
	def __inif__(self,host='localhost',user='root',password='password',port=3306,db='test'):
		self.host = host
		self.user = user
		self.password = password
		self.port = port 
		self.db = db
		self.conn = None
		self.cur = None
		

	def createConnection(self):
		try:	
			self.conn = MySQLdb.connection(host=self.host,user=self.user,passwd=self.password,db=self.db,port=self.db)
			self.cur = self.conn.cursor()
		except:
			print 'connection mysql failed!'

	def selectDB(self,colList,tableName,conditions):
		'''Only support select one table,the colList is you want to select '''
		
		cols = ''
		if len(colList):
			colsO = ''
			for col in iter(colList):
				colsO += col
				colsO += ','
			cols = colsO[:-1]
		try:
			res = self.cur.execute("select %s from %s %s" % (cols,tableName,conditions))
			return self.cur.fetchone()
		except:
			print "SQL error"

	def closeConnection(self):
		try:
			self.cur.close()
			self.conn.close()
		except:
			print "error"
		finally:
			self.cur = None
			self.conn = None
