"""
Parses metalsupermarkets' table of sheet metal gauges to create a json
formatted to have each material as an inner object, and the various
gauge-to-millimeter thicknesses as the key-values within.
"""

# for viewing pages (if not pure html)
from selenium import webdriver # remember to install the "geckodriver" firefox driver! (and include it in $PATH)
from selenium.webdriver.common.keys import Keys
# for traversing/parsing pages once html
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
# for working with our data
import os # for file system
import re # for regex
import json # for json
# from tabulate import tabulate # for prettyprint to screen (but as tables tho)

def main(debug=False):
	# data resource
	url = "https://www.metalsupermarkets.com/sheet-metal-gauge-chart/"

	if debug:
		print("opening website...")

	# create a new browser session
	driver = webdriver.Firefox()
	# pause for dramatic effect
	driver.implicitly_wait(15)
	# load page into session
	driver.get(url)

	# extract page in question as (l)xml
	# NOTE: lxml for better/more stable parsing
	soup_page = BeautifulSoup(driver.page_source, 'lxml')

	if debug:
		print("finding tables...")

	# extract all <table></table> nodes from the page
	material_tables_raw = soup_page.find_all('table')

	if debug:
		print("...found tables")

	# done with session, so better close it
	driver.quit()

	if debug:
		print("...closing website")
	
	if debug:
		print("parsing data...")

	# prepare our overall hash
	params = {}

	# loop through each table we found
	for ii in range(len(material_tables_raw)):
		# separate data and title
		table_as_html = material_tables_raw[ii]
		title_as_html = table_as_html.tr.extract()

		# convert types
		table_as_object = pd.read_html(str(table_as_html), header=0)
		title_as_string = str(title_as_html)

		# isolate title
		search_as_regex = '(?<=<td align="center" colspan="3"><strong>).+(?= Gauge Chart)' 
		# NOTE: A note on the regex formulation:
		#   "Match any characters as few as possible in bewtween "<tag nonsense>" and " Gauge Chart" is found, without counting the components in ()."
		search_results = re.search(search_as_regex, title_as_string)
		title = search_results.group(0)

		# delete imperial units
		table_values = table_as_object[0].values
		# table_values = np.delete(table_values, 1, 1) # delete the "1" element along the "1" axis (equivTo: index 1 along column space)
		# actually didn't need to delete this column, since I could later just index 0 and 2 to compensate

		# create and populate mini hash
		mini_hash = {}
		for ii in range(len(table_values)):
			# prepare our key-value pair
			key = table_values[ii][0]
			value = table_values[ii][2]

			# append the key-value pair
			mini_hash[int(key)] = round(value, 3)
		
		# add mini hash to overall hash
		params[title] = mini_hash

	if debug:
		print("...parsed data")
	
	if debug:
		print("saving to json...")

	# jsonify our hash
	params_as_json = json.dumps(params)

	# write to file
	path = os.getcwd()
	f = open(path + "\\params.json", "w")
	f.write(params_as_json)
	f.close()

	if debug:
		print("...saved to json")



if __name__ == "__main__":
	main(debug=True)