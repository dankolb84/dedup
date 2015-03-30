#! /usr/bin/python

#for to check files, get md5, filesize, name, etc, and move duplicates
import argparse
import os
import sys
import sqlite3
import hashlib

class dup_db:
	db_file = ''
	conn = ''
	def __init__(self, db_file="dup.db", table_name="dup"):
		conn = sqlite3.connect(db_file)
		c = conn.cursor()
		c.execute('select name from sqlite_master\
				 where type="table" and name="%s"'\
				  % (table_name))
		if not c.fetchone():
			#if the table does not exist, create it
			c.execute('create table dup(filename varchar(50),\
					filepath varchar(256),\
					filesize integer,\
					lfile_modified text,\
					md5sum varchar(128))')
			conn.commit()

		self.db_file = db_file
		self.db_table = table_name
		conn.close()

	def add_val(self, file_data):
		conn = sqlite3.connect(self.db_file)
		c = conn.cursor()
		print file_data
		c.execute('select * from %s where filepath="%s"' % (\
			self.db_table,
			file_data["path"]))
		if c.fetchone() == None:
			print file_data
			c.execute("insert into dup(filename, filepath, filesize, lfile_modified, md5sum)\
							 values(?,?,?,?,?)",
							(str(file_data["name"]), 
							str(file_data["path"]), 
							str(file_data["fileSize"]), 
							str(file_data["last_modified"]), 
							str(file_data["md5sum"])))
			conn.commit()
			conn.close()
def get_md5(filename, blocksize=65536):
	#print os.path.abspath(filename)
	with open(os.path.abspath(filename), 'rb') as aFile:
		aHash = hashlib.md5()
		buf = aFile.read(blocksize)
		while len(buf) > 0:
			aHash.update(buf)
			buf = aFile.read(blocksize)
	return aHash.hexdigest()

def parse_args():
	parser= argparse.ArgumentParser(description="check for duplicates")
	parser.add_argument('--inpath',
						'-i',
						type=str,
						help="Directory to begin recursion")
	parser.add_argument('--outpath',
						'-o',
						type=str,
						help="File output directory")
	parser.add_argument('--debug',
						'-d',
						action="store_true",
						help="debug flag")
	parser.add_argument('--database',
						'-s',
						type=str,
						help="Name of sqlite database table")
	parser.add_argument('--file',
						'-f',
						type=str,
						help="Name of sqlite database file")
	parser.add_argument('--exclude',
						'-x',
						nargs='*',
						help="List of excludes")
	return parser.parse_args()

def iterate_files(db_obj, args):
	#iterates through files within the path to get details
	inPath = ''
	outPath = ''
	exclude = ''

	if args["inpath"] != None:
		inPath = args["inpath"]
	else:
		inPath = "."
	
	if args["exclude"] != None:
		exclude = args["exclude"]

	if args["outpath"] != None:
		outPath = args["outpath"]
		if not os.path.isdir(outPath):
			print "outPath must be valid directory"
			exit(1)

	for root, dirs, files in os.walk(inPath):
		if len(exclude) > 0:
			for exclusion in exclude:
				if exclusion in dirs:
					dirs.remove(exclusion)
		for name in files:
			aFile = os.path.abspath(os.path.join(root,name))
			#print aFile
			fData = os.stat(aFile)
			file_data={}
			file_data["name"] = name
			file_data["path"] = aFile 
			file_data["fileSize"] = fData[6]
			file_data["last_modified"] = fData[8]
			file_data["md5sum"] = get_md5(aFile)
			db_obj.add_val(file_data)

def main():
	args=dict(vars(parse_args()))
	db_conn = dup_db()
	iterate_files(db_obj=db_conn, args=args)
	
if __name__ == "__main__":
	main()
