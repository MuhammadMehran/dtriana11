from selenium import webdriver
import time
import pandas as pd
import sys
from bs4 import BeautifulSoup
from pandas.io.json import json_normalize
filename = sys.argv[1]

df = pd.read_excel(filename)
days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

driver = webdriver.Chrome()

def scrape_info(q):
	driver.get('https://www.google.com/search?q='+q)
	try:
        link = driver.find_element_by_xpath('//a[text()="Change to English"]').get_attribute('href')
        driver.get(link)
    except:
        pass
	rating = ''
	address = ''
	daily_hours = []
	phone = ''
	price = ''
	facebook_rating = ''
	peak_time = []
	typical_spend = ''
	events_list = []
	des = ''
	neighborhood = ''
	try:
		des = driver.find_element_by_id('rhs').find_element_by_xpath('//div[@data-md="30"]').find_element_by_xpath('../..').get_attribute('innerText').split('\n')[0]
	except:
		pass
	try:
		rating = driver.find_element_by_xpath('//*[@id="rhs"]/div/div[1]/div/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div/g-review-stars/span').get_attribute('aria-label').split(' ')[1]
	except:
		pass
	try:
		address = driver.find_element_by_id('rhs').find_element_by_xpath('//a[text()="Address"]').find_element_by_xpath('../..').get_attribute('innerText').split(':')[1].strip()
	except:
		pass
	try:
		table = driver.find_element_by_id('rhs').find_element_by_xpath('//a[text()="Hours"]').find_element_by_xpath('../..').find_element_by_tag_name('tbody')
		trs = table.find_elements_by_tag_name('tr')
		for tr in trs:
			soup = BeautifulSoup(tr.get_attribute('innerHTML'))
			hr = ''
			for td in soup.findAll('td'):
				hr += td.text + ' '
			data = {}
			data['name'] = q
			data['day'] = hr.split(' ')[0]
			try:
				data['open'] = hr.split(' ')[1].split('–')[0]
				data['close'] = hr.split(' ')[1].split('–')[1]
			except:
				pass
			
			daily_hours.append(data)
		# daily_hours = driver.find_element_by_id('rhs').find_element_by_xpath('//a[text()="Hours"]').find_element_by_xpath('../..').get_attribute('innerText').split(':')[1].strip()
	except:
		pass
	try:
		phone = driver.find_element_by_id('rhs').find_element_by_xpath('//a[text()="Phone"]').find_element_by_xpath('../..').get_attribute('innerText').split(':')[1].strip()
	except:
		pass
	try:
		price = driver.find_element_by_xpath('//*[@id="rhs"]/div/div[1]/div/div[1]/div/div[1]/div[2]/div[2]/div[3]/div/span[1]').get_attribute('innerText')
	except:
		pass
	try:
		facebook_rating = driver.find_element_by_id('rhs').find_element_by_xpath('//span[@data-original-name="Reviews from the web"]').find_element_by_xpath('..').find_element_by_xpath('following-sibling::div').find_element_by_xpath('//span[text()="Facebook"]').find_element_by_xpath('preceding-sibling::span').get_attribute('innerText')
	except:
		try:
			facebook_rating = driver.find_element_by_id('rhs').find_element_by_xpath('//span[@data-original-name="Reviews from the web"]').find_element_by_xpath('..').find_element_by_xpath('following-sibling::div').find_element_by_xpath('//span[text()="Facebook"]').find_element_by_xpath('following-sibling::span').get_attribute('innerText')
		except:
			pass
	try:
		for i in range(0,7):
			peak_time.append(days[i]+': '+driver.find_element_by_id('rhs').find_element_by_xpath('//div[text()="Plan your visit"]').find_element_by_xpath('following-sibling::div').find_element_by_xpath('//div[@data-day-of-week="'+str(i)+'"]').get_attribute('innerText'))
		# peak_time = driver.find_element_by_id('rhs').find_element_by_xpath('//div[text()="Plan your visit"]').find_element_by_xpath('following-sibling::div').get_attribute('innerText')
	except:
		pass
	try:
		typical_spend = driver.find_element_by_id('rhs').find_element_by_xpath('//div[@data-attrid="kc:/local:plan your visit"]').get_attribute('innerText').split('spend')[1].strip()
	except:
		pass
	try:
		events_link = driver.find_element_by_id('rhs').find_element_by_xpath('//a[text()="Events"]').get_attribute('href')
		driver.get(events_link)
		events = driver.find_elements_by_class_name('rl_item_base')
		for event in events:
			data = {}
			data['name'] = q
			try:
				if len(event.get_attribute('innerText').strip().split('\n')) == 3:
					data['date'] = event.get_attribute('innerText').split('\n')[0]
					data['time'] = event.get_attribute('innerText').split('\n')[1]
					data['event name'] = event.get_attribute('innerText').split('\n')[2]
				else:
					data['date'] = event.get_attribute('innerText').split('\n')[0]
					data['event name'] = event.get_attribute('innerText').split('\n')[1]
				events_list.append(data) 
			except:
				pass
			events_list.append(data)
	except:
		pass
	driver.get('https://www.google.com/search?q='+q+' neighborhood')
	try:
		neighborhood = driver.find_element_by_xpath('//h2[text()="Map results"]').find_element_by_xpath('..').find_element_by_class_name('desktop-title-content').get_attribute('innerText')
	except:
		pass
	return des, rating, address, daily_hours, phone, price, facebook_rating, ','.join(peak_time), typical_spend, events_list, neighborhood

addresses = []
phones = []
descriptions = []
google_reviews = []
facebook_reviews = []
prices = []
events = []
daily_hourss = []
peak_hours = []
typical_sends = []
neighborhoods = []
for index, row in df.iterrows():
	q = row['Name'] + ' ' + row['City'] + ' ' + row['Country']
	print('Scrapping',row['Name'])
	des, rating, address, daily_hours, phone, price, facebook_rating, peak_time, typical_spend, events_list, neighborhood = scrape_info(q)
	addresses.append(address)
	phones.append(phone)
	descriptions.append(des)
	google_reviews.append(rating)
	facebook_reviews.append(facebook_rating)
	prices.append(price)
	events.extend(events_list)
	daily_hourss.extend(daily_hours)
	peak_hours.append(peak_time)
	typical_sends.append(typical_spend)
	neighborhoods.append(neighborhood)
	time.sleep(2)


driver.quit()
df2 = pd.DataFrame(zip(addresses,phones,descriptions,neighborhoods,google_reviews,facebook_reviews,prices,typical_sends)
				  , columns=['Address','Phone','Description','Neighborhood','Google Reviews','Facebook Reviews','Price','Typical Send'])

df3 = pd.concat([df,df2],axis=1)

df4 = json_normalize(daily_hourss)
df5 = json_normalize(events)

writer = pd.ExcelWriter(filename, engine='xlsxwriter')
df3.to_excel(writer,sheet_name = 'Data', index=False)
df4.to_excel(writer,sheet_name = 'Daily Hours', index=False)
df5.to_excel(writer,sheet_name = 'Events', index=False)
writer.save() 