import requests
import urllib
from bs4 import BeautifulSoup
import os
import pprint
# Globals
hostname = "http://www.bits-pilani.ac.in/"
semester_list_url = "TPClassRoomRecording/"
tp_page_url = "/TPClassRoomRecording/index.aspx?Folder=G%3a%5cTPClassRoomRecording%5cVideo"
downloads_path = "Downloaded/"	

def parse_for_video_urls(url):
	html_home = requests.get(url)
	parser = BeautifulSoup(html_home.text,"html.parser")
	video_urls = parser.findAll('a')
	
	return_urls = []
	for href in video_urls:
		if href['href'].endswith(".wmv"):
			return_urls.append(href)
			

	return return_urls


def download_course(url,sem):
	
	html_home = requests.get(url)

	parser = BeautifulSoup(html_home.text,"html.parser")

	video_urls = parser.findAll('a')

	if len(video_urls) == 0:
		print "NO videos found"
		return

	course_code = url.split('%5c')[-1].replace('+',' ')
	
	if not os.path.exists(downloads_path):
		os.mkdir(downloads_path)

	if not os.path.exists(downloads_path+"/"+course_code):
		os.mkdir(downloads_path+"/"+course_code)
	

	files = os.listdir(downloads_path+"/"+course_code)

	print "Get files in " + downloads_path+"/"+course_code
	"""
	Remove already downloaded videos from the download queue
	"""

	print "Files to download " + str(len(video_urls))

	dup = 0

	# Remove already downloaded file
	for f in files:
		for href in video_urls:
			if f == href.text +"_"+href['href'].split("\\")[-1]:
				video_urls.remove(href)
				dup+=1

	print "Duplicates removed " + str(dup)

	for href in video_urls:
		if "wmv" not in href['href']:
			continue		

		filename = href.text +"_"+href['href'].split("\\")[-1]
	 	urllib.urlretrieve(href['href'], filename=downloads_path+"/"+course_code+"/"+filename)
	 	print("Download complete "+filename)

				
def getAllCourses(semester):
	
	courses = {}	
	for sem in semester:
		courses[sem] = getCourseForSemester(sem)

	return courses

def getCourseForSemester(semester):
	
	response = requests.get(hostname+tp_page_url+"/"+semester)
	bs = BeautifulSoup(response.text,"html.parser")
	hrefs = bs.find('div',{"id":"FolderView1_folder_view"}).findAll('a')
	course_code = [x.text for x in hrefs]	

	return course_code

"""
Allows users to choose the semester and course to download
"""

def get_all_video_urls():
	video_urls = []
	"""
	Scrape for semesters
	"""

	response = requests.get(hostname+semester_list_url)

	soup = BeautifulSoup(response.text,"html.parser")

	content = soup.find('div',{'id':'FolderView1_folder_view'})

	href_semester = content.findAll('a')
	href_semester = [x.text for x in href_semester]

	for x in href_semester:				
		courses = getCourseForSemester(x.replace(" ","+"))
		for c in courses:
			urls = parse_for_video_urls(hostname+tp_page_url+"%5c"+x+"%5c"+c)		
			
			for url in urls:

				document = {}
				document['course_code'] = c
				document['semester'] = x
				document['url'] = url['href']
				document['name'] = url.text


				video_urls.append(document)

	import json
	#json_string = json.dumps(video_urls)
	with open('data.json', 'w') as fp:    	
		json.dump(video_urls,fp)






def main():
	
	"""
	User input for semeser and course	
	"""

	response = requests.get(hostname+semester_list_url)

	soup = BeautifulSoup(response.text,"html.parser")

	content = soup.find('div',{'id':'FolderView1_folder_view'})

	href_semester = content.findAll('a')
	href_semester = [x.text for x in href_semester]

	print("Available Semester Choices ")

	for x in range(0,len(href_semester)):
		statement = """{0}) {1}"""
		print(statement.format(x+1,href_semester[x]))

	# Chose a semster	
	chosen_semester = input("Choose semester :")

	
	# List all courses for the semester
	print("Listing courses for semester : {0}".format(href_semester[chosen_semester-1]))


	courses = getCourseForSemester(href_semester[chosen_semester-1].replace(" ","+"))

	for x in range(0,len(courses)):
		statement = """{0}) {1}"""
		print(statement.format(x+1,courses[x]))

	chosen_course = input("Choose course : ")

	course = courses[chosen_course-1]
	sem = href_semester[chosen_semester-1].replace(" ","+")

	print "Starting Course : "+course
	download_course(hostname+tp_page_url+"%5c"+sem+"%5c"+course,sem.replace("+"," "))
	print "Course Complete : "+course


if __name__ == '__main__':
	#main()
	get_all_video_urls()