from bs4 import BeautifulSoup
import requests, json, re, urllib.request, magic, os
import my_file

all_results = []
subjects_dict = {}

# FUNCTION: Write each item data and normalized date as dictionary to list "all_results"

def addItem(title, thumbnail, url, institution, object_date, subjects, medium, type, my_source, creator=None):
	good_date_format = re.compile('\d{4}')
	slash_date_format = re.compile('\d*/\d*/\d{2}')
	if good_date_format.match(object_date):
		date_normalized = object_date[:4]
	elif good_date_format.search(object_date):
		year_search = good_date_format.search(object_date)
		date_normalized = year_search.group()
# this will maybe need to be rethought because it is a hack: assuming 1800s
	elif slash_date_format.search(object_date):
		year_search = slash_date_format.search(object_date)
		date_normalized = year_search.group()
		date_normalized = date_normalized[-2:]
		date_normalized = "18"+date_normalized		
	else:
		date_normalized = "unknown"
	for subject in subjects:
		if subject in subjects_dict:
			subjects_dict[subject] = subjects_dict[subject]+1
		else:
  			subjects_dict[subject]=1		
	item_dict = { 		'title': title,
						'thumbnail': thumbnail,
						'url': url,
						'institution': institution,
						'object_date': object_date,
						'norm_date': date_normalized,
						'subjects': subjects,						
						'medium': medium,
						'type': type,
						'my_source': my_source	}
	if creator:
		item_dict['creator'] = creator										
	if thumbnail != 'unknown':
		try:
			thumb_match = re.compile('(.*)/(.*.jpg$)')
			thumb = thumb_match.search(thumbnail)	
			file = "thumbnails/"+thumb.group(2)
		except:
			try:
				thumb_match = re.compile('(.*)/(.*.gif$)')
				thumb = thumb_match.search(thumbnail)	
				file = "thumbnails/"+thumb.group(2)
			except:
				try:
					thumb_match = re.compile('(.*)/.*/(.*)(/thumbnail$)')
					thumb = thumb_match.search(thumbnail)						
					file = "thumbnails/"+thumb.group(2)					
				except:
					try:
						thumb_match = re.compile('(.*id/)(.*)')
						thumb = thumb_match.search(thumbnail)
						file = "thumbnails/"+thumb.group(2)	
					except:
# NYPL
						try:
							thumb_match = re.compile('(.*id=)(.*)(&t=t)')
							thumb = thumb_match.search(thumbnail)
							file = "thumbnails/"+thumb.group(2)
						except:
							pass								
	
		urllib.request.urlretrieve(thumbnail, file)
# check for thumbs no extension		
		if '.' not in file and os.path.isfile(file):
			mime = magic.from_file(file, mime=True)
#			print(mime)
			extension_match = re.compile(b'(.*)/(.*)')				
			extension = extension_match.search(mime)
			extension = str(extension.group(2))
			extension = extension[2:]
			extension = extension[:-1]
			new_filename = file+'.'+extension
#			print(new_filename)
			os.rename(file, new_filename)
			file = str(new_filename)
		file = file.replace('thumbnails/','')
#		print (file)
	else:
		file = 'noimg.png'		
	item_dict['local_thumbnail'] = file	
# create temp list to monitor progress																	
	with open("exclusion_master_running","a") as file:
		file.write(str(item_dict)) 
# push dict to list for final write at end								
	all_results.append(item_dict)
	
# FUNCTION: CALIFORNIA STATE PARKS (COLLECTION: ANGEL ISLAND CHINESE IMMIGRATION CERTIFICATES)
# get info from page for certificate and parse person detail page

def getCSPInfo (url, soup):
#	print ('CSP certificate item')
	institution = "California State Parks, State Museum Resource Center"
	medium = 'certificate'
	type = 'image'
	title = re.compile('Object Name:.*?<td>(.*?)</td>')
	owner_info = re.compile('Original Owner:</strong></td><td><a href="(.*?)">(.*?)</a>')
	title3 = re.compile('Original Owner:</strong></td><td><a.*?>.*?</a>(,.*?)</td>')
	subjects_string = re.compile('Subject:.*?<td>(.*?)</td>')
	soup_string = str(soup.html)
	title_matches = title.search(soup_string)	
	owner_string = owner_info.search(soup_string)
	title2_string = owner_string.group(2)	
	if (title3.search(soup_string)):
		title3_string = title3.search(soup_string)
		title3_string = title3_string.group(1)
		title2_string = title2_string+title3_string
	title = title2_string+ " ("+title_matches.group(1)+")"
	print (title)
	subjects_match = subjects_string.search(soup_string)
	subjects = subjects_match.group(1).replace(';',',')
	subjects = [x.strip() for x in subjects.split(',')]
# dig into person page text for date
	person_url = owner_string.group(1)
	person_url = person_url.replace('amp;', '')	
	person_url = "http://www.museumcollections.parks.ca.gov/code/"+person_url
#	print (person_url)
	person_page = requests.get(person_url) 
	person_html = person_page.text
	person_soup = BeautifulSoup(person_html)	
	person_soup_string = str(person_soup.html)
	object_date = ''
#	print (person_soup_string)
	date_word_anchors = [' arrived ', ' came ', ' immigrated ']	
	for anchor in date_word_anchors:
#		print(anchor)
		if (object_date == ''):
			date_match = re.compile(anchor+'.*?(\d\d\d\d)')
			date_string = date_match.search(person_soup_string)		
			try:
				object_date = date_string.group(1)
#				print (anchor+": "+object_date)
			except:
				print (anchor+": not found")		
	images = soup.find_all('img')
	for image in images:
		if "http://www.museumcollections.parks.ca.gov/media/previews/" in image['src']:
			thumbnail = image['src']
			img = thumbnail.replace('previews', 'full')
	my_source = 'CSP'
	creator = 'Angel Island Immigration Station'		
	addItem(title, thumbnail, url, institution, object_date, subjects, medium, type, my_source, creator)	


# FUNCTION: CALIFORNIA STATE PARKS (COLLECTION: ANGEL ISLAND IMMIGRATION STATION)
# get info from page for photo

def getCSPInfo2 (url, soup):
	institution = "California State Parks, State Museum Resource Center"
	medium = 'lantern slide'
	type = 'image'
	title = re.compile('Description:.*?<td>(.*?)</td>')
	date = re.compile('Date:.*?<td>(.*?)</td>')
	subjects_string = re.compile('Subject:.*?<td>(.*?)</td>')	
	doc_type = 'image'
	soup_string = str(soup.html)
	title_matches = title.search(soup_string)
	try:	
		title = title_matches.group(1)
	except AttributeError:
		title = 'Untitled'
	print(title)		
	subjects_match = subjects_string.search(soup_string)
	subjects = subjects_match.group(1).replace(';',',')
	if 'chinese' in subjects.lower() or 'chinese' in title.lower():
		date_matches = date.search(soup_string)
		try:	
			object_date = date_matches.group(1)
		except AttributeError:
		 object_date = 'No date'	
		if subjects.endswith('<br/>'):
			subjects = subjects[:-5]	
		subjects = [x.strip() for x in subjects.split(',')]			
		images = soup.find_all('img')
		for image in images:
			if "http://www.museumcollections.parks.ca.gov/media/previews/" in image['src']:
				thumbnail = image['src']
				img = thumbnail.replace('previews', 'full')
		my_source = 'CSP'
		creator = 'Angel Island SP'		
		addItem(title, thumbnail, url, institution, object_date, subjects, medium, type, my_source, creator)


##### CALISPHERE ########### (so far only the image items, not the text items....)
calisphere = requests.get('http://content.cdlib.org/search?facet=type-tab&relation=calisphere.universityofcalifornia.edu&style=cui&keyword=chinese+exclusion+act&x=0&y=0&rmode=json')
#print(calisphere.status_code)

# run Calisphere into a python dictonary
c_data = json.loads(calisphere.text)

#json.dump(c_data, open("exclusion_results.txt",'w'))

# format Calisphere as Python dic
# print (c_data) #prints all in dictionary
#print (c_data['api']) #prints api key=>values literally
calisphere_set = c_data['objset']
for item in calisphere_set:	
	thumbnail = item['files']['thumbnail']['src']		
	url	= item['qdc']['identifier']
	url = url[0]
	title = item['qdc']['title']
	if (isinstance(title, list)):
		title = title[0]
	print(title)	
	institution = item['courtesy_of']
	try:
		object_date = item['qdc']['date']['v']
	except TypeError:
		object_date = item['qdc']['date']
	except KeyError:
		object_date = item['qdc']['identifier']
		object_date = object_date[1]
		object_date = object_date['v']
	subjects = item['qdc']['subject']
	new_subjects = []
	for subject in subjects:
		if isinstance(subject, str):
#			print (subject)
#			print ("is a string")
			try:			
				split_subjects = [x.strip() for x in subject.split(';')]									
				for new_subject in split_subjects:
					new_subject= re.sub(r'\s', ' ', new_subject)
					new_subject= re.sub('\n', '', new_subject)
					new_subject=re.sub(' +',' ', new_subject)					
					new_subjects.append(str(new_subject))
			except:
				pass
		else:
			new_subjects.append(subject['v'])
	new_subjects = list(filter(None, new_subjects))
#	for s in new_subjects:
#		print (s)
	type = 'image'
	if isinstance(item['qdc']['format'], list):
		item_format = item['qdc']['format']
		medium = item_format[0]
	else:
		medium = 'unknown'
	my_source = 'Calisphere'			
	addItem(title, thumbnail, url, institution, object_date, new_subjects, medium, type, my_source )

####### DPLA ############
payload = {'q': 'chinese+exclusion+act', 'page_size': 10000,  'api_key': my_file.dpla}
dpla = requests.get('http://api.dp.la/v2/items', params=payload)

#print(dpla.status_code)

# run it into a python dictionary
dpla_data = json.loads(dpla.text)

for item in dpla_data['docs']:
	title = item['sourceResource']['title']
	if isinstance (title, list):
   		title = title[0]
	print (title)		
	try:
		thumbnail = item['originalRecord']['objects']['object']
		try:
			thumbnail = thumbnail[0]
			thumbnail = thumbnail['thumbnail-url']
		except KeyError:
			thumbnail = thumbnail['thumbnail-url']					
	except KeyError:
		if 'object' in item:
			thumbnail = item['object']
		else:		
			thumbnail="unknown"
# Some Hathi from Purdue have no thumb		
	url= item['isShownAt']
	institution = item['provider']['name']					
	try:
		object_date = item['sourceResource']['date']['displayDate']
# this line solely for one object 'Changing socio-cultural patterns'
		try:
			date_test = item['originalRecord']['date']
			if isinstance (date_test, list):
				object_date = item['originalRecord']['date']
				object_date = object_date[0]
		except:
			pass		
	except KeyError:
		object_date = item['originalRecord']['hierarchy']['hierarchy-item']
		object_date = object_date[0]
		object_date = object_date['hierarchy-item-inclusive-dates']			
	try:
		item_creator = item['sourceResource']['creator']
		if isinstance (item_creator, list):
			item_creator = item_creator[0]			
	except:
		try:
			item_creator = item['sourceResource']['publisher']
			item_creator = item_creator[0]
		except:
			pass
	subjects = []	
	try:
		item['sourceResource']['subject']
		for subject in item['sourceResource']['subject']:
			if isinstance(subject, str):
				subjects.append(subject)
			else:
				if isinstance(subject, dict):
					subjects.append(subject['name'])			
	except KeyError:
		subjects.append('NO SUBJECTS HERE')											
# check if type exists
	try:
		type = item['sourceResource']['type']
	except KeyError:
		type = 'unknown'
# check medium  		
	try:
		medium = item['originalRecord']['physical-occurrences']['physical-occurrence']['media-occurrences']['media-occurrence']['media-type']
	except:
		medium= 'unknown'
	my_source = 'DPLA'	 		
	addItem(title, thumbnail, url, institution, object_date, subjects, medium, type, my_source, item_creator)


csp_url = "http://www.museumcollections.parks.ca.gov/code/emuseum.asp?collection=6002&collectionname=Angel%20Island%20Chinese%20Immigration%20Certificates&style=Browse&currentrecord=1&page=collection&profile=objects&searchdesc=Angel%20Island%20Chinese%20Immigration%20Certificates&action=collection&style=single&currentrecord=1"
while (csp_url):
#	print (csp_url)
	item_page = requests.get(csp_url) 
	item_html = item_page.text
	soup = BeautifulSoup(item_html)
	getCSPInfo(csp_url, soup)
	results_div = soup.find(id='navwrapper')
	results_div = results_div.find_all('a')
#	print (results_div)
	next_link=''
	for result in results_div:
		if result.string:
			if 'next' in result.string:
				if (result['href']):
					next_link = result['href']
					csp_url = "http://www.museumcollections.parks.ca.gov/code/"+next_link
	if next_link == '':
		csp_url = False	

csp_url2 = "http://www.museumcollections.parks.ca.gov/code/emuseum.asp?collection=4120&collectionname=Angel%20Island%20Immigration%20Station&style=single&currentrecord=11&page=collection&profile=objects&searchdesc=Angel%20Island%20Immigration%20Station&action=collection&currentrecord=1"
while (csp_url2):
#	print (csp_url2)
	item_page = requests.get(csp_url2) 
	item_html = item_page.text
	soup = BeautifulSoup(item_html)
	getCSPInfo2(csp_url2, soup)
	results_div = soup.find(id='navwrapper')
	results_div = results_div.find_all('a')
#	print (results_div)
	next_link=''
	for result in results_div:
		if result.string:
			if 'next' in result.string:
				if (result['href']):
					next_link = result['href']
					csp_url2 = "http://www.museumcollections.parks.ca.gov/code/"+next_link
	if next_link == '':
		csp_url2 = False

# PRINT ALL SUBJECTS
with open("master_subjects","w") as subjects_list:
	for subject_key in subjects_dict:
		subjects_list.write("'"+subject_key+"',"+str(subjects_dict[subject_key])+"\n")

with open("master_final","w") as results_list:
	json.dump(all_results, results_list, indent = 4, ensure_ascii=False)

			
# MAKE WEB PAGE
with open("exclusion.html","w") as webpage:
	webpage.write("<HTML><HEAD><TITLE>Exclusion Mash-Up</TITLE></HEAD>")
	webpage.write("<BODY>")
	from operator import itemgetter
	all_results.sort(key=itemgetter('norm_date'), reverse=False)	
	for result in all_results:
		webpage.write("<A HREF='"+result['url']+"'><IMG SRC='thumbnails/"+result['local_thumbnail']+"' WIDTH='120'></A>\n")
	webpage.write("</BODY></HTML>")  					

