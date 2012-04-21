import sys
import os
import urllib2
import re
import codecs
import time
import BeautifulSoup

def getbookinfo(baseurl, html):
	soup = BeautifulSoup.BeautifulSoup(html)
	table = soup.find('table', border='2', cellpadding='3', width='80%')
	rows = table.findAll('tr')
	for row in rows[1:]:
		titleandlink = row.contents[1]
		author = row.contents[3].text
		pages = row.contents[5].text
		title = titleandlink.text
		selectionregex = re.compile(r'^\.\./manuscript/.*')
		anchortag = titleandlink.find('a', href=selectionregex)
		link = anchortag.attrMap['href'].rpartition('/')[0]
		if baseurl[-1] == '/':
			link = baseurl + link
		else:
			link = baseurl + '/' + link
		print title
		print author
		print pages
		print link
		yield title, author, pages, link

def downloadpages(link, start, count, targetdestination):
	for i in xrange(0, count):
		pagelink = link + '/' + str(start + i)
		try:
			response = urllib2.urlopen(pagelink)
		except:
			print 'Failed to download %s. Skipping...' % pagelink
			continue
		else:
			html = response.read()
			soup = BeautifulSoup.BeautifulSoup(html)
			anchortag = soup.find('a', id='ctl00_ContentPlaceHolder1_imageLink')
			imagelink = anchortag.attrMap['href']
			imagefilename = imagelink.split('/')[-1]
			print 'Downloading image %s to file %s' % (imagelink, imagefilename)
			with open(os.path.join(targetdestination, imagefilename), 'wb') as imagefile:
				try:
					imageresponse = urllib2.urlopen(imagelink)
					image = imageresponse.read()
					imagefile.write(image)
					imagefile.close()
				except:
					print 'Failed to download %s' % imagelink
		pausetime = 1
		print 'Sleeping for %d second(s) before requesting the next image...' % pausetime
		time.sleep(pausetime)
	
def setupbook(rootfolder, title, author, pages, link):
	currentfolderpath = os.path.join(rootfolder, title)
	# check if the target folder exists.
	if not os.path.exists(os.path.join(rootfolder, title)):
		os.mkdir(os.path.join(rootfolder, title))
	# check if book metadata exists in the target folder.
	metadatafile = os.path.join(currentfolderpath, ".meta")
	if not os.path.exists(metadatafile):
		with codecs.open(metadatafile, 'w', encoding='utf-8') as metafile:
			metafile.write(','.join([title, author, pages, link]))
			metafile.close()
	
	filesalreadydownloaded = 0
	for root, dirs, files in os.walk(currentfolderpath):
		for f in files:
			currentfilepath = os.path.join(root, f)
			filename, ext = os.path.splitext(f)
			if ext == ".JPG":
				filesalreadydownloaded += 1
	return currentfolderpath, filesalreadydownloaded
	
def main():
	rootfolder = sys.argv[1]
	print 'using %s as root folder' % rootfolder

	# make sure the root folder exists.
	if not os.path.isdir(rootfolder):
		os.mkdir(rootfolder)

    baseurl = 'www.new1.dli.ernet.in/cgi-bin/advsearch_db.cgi?listStart=%d&language1=Urdu&perPage=%d'
	# baseurl = "http://makhtota.ksu.edu.sa/"
	# browseurl = baseurl + 'eBrowse/'
	stepSize = 20
	
	for currentindex in xrange(0, 1000, stepSize):
		# currenturl = browseurl + str(currentindex)
		currenturl =  baseurl % (currentIndex, stepSize)
		print 'fetching %s' % currenturl
		currentbookgroupfolder = str(currentindex) + '-' + str(currentindex + stepSize - 1)
		currentbookgrouppath = os.path.join(rootfolder, currentbookgroupfolder)
		if not os.path.exists(currentbookgrouppath):
			os.mkdir(currentbookgrouppath)
		try:
			response = urllib2.urlopen(currenturl)
		except:
			print 'Failed to fetch data for index %d. Skipping...' % currentindex
			continue
		html = response.read()
		for title, author, pages, link in getbookinfo(browseurl, html):
			currentbookpath, filesalreadydownloaded = setupbook(currentbookgrouppath, title, author, pages, link)
			downloadpages(link, filesalreadydownloaded + 1, int(pages) - filesalreadydownloaded, currentbookpath)
		
		pausetime = 10
		print 'Sleeping for %d seconds before downloading new batch...' % pausetime
		time.sleep(pausetime)
		
if __name__ == "__main__":
	main()

