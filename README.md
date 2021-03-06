This Python 3.4 script is an attempt to build a simple web page of primary sources for a single subject. It queries resources in digital archives and special collections to retrieve metadata. It also downloads the thumbnails and URLS for the resources. This code is written to specifically find materials on the Chinese Exclusion Act.

The goal is to test possible methods for creating a subject-based tool for researchers and also to test the reliability of the metadata obtained in using digital repository APIs and by scraping web sites. The metadata is relatively reliable, but not perfect, especially dates.

RESOURCES QUERIED<br>
The Digital Public Library of America (DPLA)<br>
Calisphere (images only)<br>
The California State Parks Museum Collections<br>

PRIMARY FILES PRODUCED<br>
A JSON dictionary with normalized metadata for each object;<br>
A raw webpage (HTML) sorted by date to troubleshoot the proper download of metadata and thumbnails;<br>
A file of subject terms collected including a count of the objects where the term appears.<br>

SECONDARY FILE PRODUCED<br>
A running file that dumps metadata for an object once processed. This is to assist in troubleshooting problem areas when running the script.

WHAT YOU NEED TO RUN THIS CODE<br>
A Python interpreter (Python 3.4)<br>
An API key for DPLA<br>
All the Python modules in the import line (except ‘my_file’)<br>
A folder in the same directory as the script called “thumbnails”<br>

The resulting page with contextualizing information and additional style formatting can be viewed at the following URL:<br>
http://pfch.nyc/quipu/project.html

HOW THIS CODE CAN BE REPURPOSED MEANINGFULLY<br>
This code is specifically written for the subject Chinese Exclusion Act. It may work for another subject, however, if you would like to use this script to begin finding resources and collecting metadata/thumbnails for your own subject, you will definitely need to change certain parts of this script:

<ul>
<li>Delete or comment out any lines that pertain to the California State Parks website.</li>
<li>For DPLA, you will need to insert your API key and change the API query to reflect your subject instead of ‘Chinese Exclusion Act’ in the following lines, as indicated:<br><br>

<i>{'q': ‘your+subject+phrase+here’, 'page_size': 10000,  'api_key': ‘your_API_key_here’ }</i><br>
	<i>dpla = requests.get('http://api.dp.la/v2/items', params=payload)</i>
</li><br>
<li>For Calisphere, you will need to replace ‘Chinese Exclusion Act’ with your subject in the following line, as indicated:<br><br>

<i>calisphere = requests.get('http://content.cdlib.org/search?facet=type-tab&relation=calisphere.universityofcalifornia.edu&style=cui&keyword=your+subject+here&x=0&y=0&rmode=json')</i>
</li>
</ul>

*** Code and metadata should be checked, if you plan to use it ***<br>
*** DPLA is constantly expanding its base of content providers, which will effect the ability of this script to retrieve all metadata ***

README last updated: 12/21/2015
 
