#!/usr/bin/env python3
import time
import re
import os
import datetime
from datetime import datetime
from pytz import timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

# chrome version: 114.0.5735.106
# https://www.vacationstogo.com/fastdeal.cfm?deal=39709

def extract_price(s: str) -> str:
    '''Remove $ and , from price value.'''
    return s.replace('$', '').replace(',', '')

def extract_number(s: str) -> str:
    '''Remove % from percentage value.'''
    return re.findall(r'\d+', s)[0]

def write_to_file(itinerary, hist, deal):
    '''Wirte to a txt file'''

    print(' --- Writing to history.txt ... ---')
    file_path = os.path.expanduser("~/Documents/history.txt")

    # Get the current date
    current_date = datetime.now(timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')

    # Open the file in append mode
    with open(file_path, "a") as file:
        # Write the date
        file.write(f" --------- Updated on : {current_date} --------- \n")

        # Write
        file.write(f"#{deal}\n")
        for key, value in eval(itinerary).items(): #write itinerary details
            file.write(f"{key}: {value}\n")
        for key, values in eval(hist).items():
            formatted_values = [f"${value}" if index < 2 else f"{value}%" for index, value in enumerate(values)]
            file.write(f"{key}: {', '.join(formatted_values)}\n")
        file.write("\n")

def send_email(sender_email: str, sender_password: str, recipients_email: str, subject: str, body: str, attachment_path: str):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    #create the email
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipients_email)

    # Add the body message
    msg.attach(MIMEText(body, "plain"))

    # Attach the file
    with open(attachment_path, "r") as file:
        attachment_content = file.read()
        part = MIMEText(attachment_content)
        part.add_header("Content-Disposition", "attachment", filename='history.txt')
        msg.attach(part)

    # Connect to Gmail's SMTP server and send the email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {str(e)}")

sender_email = "codewhiz0617@gmail.com"
sender_password = "tbhwsxslhcyrrewh"
recipient_email = ["horseo0220@gmail.com"]#,"celiasxh@hotmail.com", 'peterlhq@hotmail.com']
attachment_path = "/Users/haozhili/documents/history.txt"

hist_39709: dict = {}
hist_26936: dict = {}
hist_16701: dict = {}
itinerary_39709: dict = {} # {'depart': ['sun, dec 27', 'miami, fl', '5:00pm'], 'back': [...]}
itinerary_26936: dict = {}
itinerary_16701: dict = {}

my_deals = [39709,26936,16701]
notify = False
refresh_rate = 5 #sec
did_brochure = False

body_deal: int
body_cabin: str = " "
# body_prev_pct: str = ""
# body_pct: str = ""
body_prev_price: str = " "
body_curr_price: str = " "

while True:
    # current_time = time.localtime()
    # if (current_time.tm_hour == 8 and current_time.tm_min == 0) or (current_time.tm_hour == 15 and current_time.tm_min == 0) or (current_time.tm_hour == 21 and current_time.tm_min == 20) or (current_time.tm_hour == 21 and current_time.tm_min == 21):
    # if (current_time.tm_hour == 7 and current_time.tm_min == 30) or (current_time.tm_hour == 8 and current_time.tm_min == 0) or (current_time.tm_hour == 15 and current_time.tm_min == 0):
        start_time = time.time()
        driver = webdriver.Chrome()
        driver.get('https://www.vacationstogo.com/login.cfm?profile=yes')

        # Log in
        email = "horseo0220@gmail.com"
        email_input = driver.find_element(By.XPATH, "//input[@name='LogEmail']")
        go_button = driver.find_element(By.XPATH, "//button[text()='Go!']")
        email_input.send_keys(email)
        go_button.click()

        # check to see if the login was successful
        WebDriverWait(driver, timeout=5).until(lambda x: x.find_element(By.CLASS_NAME, "bottom-half"))

        # Select the desired options in 'Find a Bargain' section
        s_month = Select(driver.find_element(By.XPATH, "//select[@id='SMonth']"))
        s_month.select_by_value('202312')
        t_month = Select(driver.find_element(By.XPATH, "//select[@id='TMonth']"))
        t_month.select_by_value('202312')
        region = Select(driver.find_element(By.XPATH, "//select[@id='RegionID']"))
        region.select_by_value('13')
        line = Select(driver.find_element(By.XPATH, "//select[@id='LineID']"))
        line.select_by_value('0') #all cruise lines
        ship = Select(driver.find_element(By.XPATH, "//select[@id='ShipID']"))
        ship.select_by_value('0') #all ships
        length = Select(driver.find_element(By.XPATH, "//select[@id='Length']"))
        length.select_by_value('1') #3-6 nights
        d_port = Select(driver.find_element(By.XPATH, "//select[@id='DPortID']"))
        d_port.select_by_value('0')
        v_port = Select(driver.find_element(By.XPATH, "//select[@id='VPortID']"))
        v_port.select_by_value('0')
        label = driver.find_element(By.XPATH,"//label[contains(text(), 'Return to same port')]")
        label.click()

        #show me the deals!
        show = driver.find_element(By.CSS_SELECTOR, "input[id=fabShowMeTheDeals]")
        show.click()
        #show deals in CAD
        cad = driver.find_element(By.PARTIAL_LINK_TEXT, "CAD$")
        cad.click()
        
        for d in my_deals:
            notify = False #by default don't send email
            body_deal = d #for record
            try: 
                if d == 39709:
                    deal = driver.find_element(By.XPATH, f'//a[text()="#{d}"]').click()
                else:
                    driver.back()
                    deal = driver.find_element(By.XPATH, f'//a[text()="#{d}"]').click()

                #store depart and back 
                FastdealItinerary = driver.find_element(By.ID, "FastdealItinerary")
                rows = FastdealItinerary.find_elements(By.TAG_NAME, "tr")
                first_row = rows[1] #depart
                last_row = rows[-1] #back
                itinerary = f"itinerary_{d}"

                # Extract the content from the first row's td elements
                first_row_tds = first_row.find_elements(By.TAG_NAME, "td")
                eval(itinerary)['Depart'] = [] # initialize the list for depart info
                for td in first_row_tds:
                    try:
                        a_element = td.find_element(By.TAG_NAME, "a")
                        if a_element:
                            eval(itinerary)['Depart'].append(a_element.text)
                    except NoSuchElementException:
                        if td.text:
                            eval(itinerary)['Depart'].append(td.text)

                # Extract the content from the last row's td elements
                last_row_tds = last_row.find_elements(By.TAG_NAME, "td")
                eval(itinerary)['Back'] = [] # initialize the list for back info
                for td in last_row_tds:
                    try:
                        a_element = td.find_element(By.TAG_NAME, "a")
                        if a_element:
                            eval(itinerary)['Back'].append(a_element.text)
                    except NoSuchElementException:
                        if td.text:
                            eval(itinerary)['Back'].append(td.text)

                print(f"depart and back info for deal {d} is {eval(itinerary)}")

                #Get the prices...
                for cabin in ["inside", "oceanview", "balcony", "suite"]:
                    body_cabin = cabin
                    if cabin == "inside" or cabin == "balcony":
                        outer_div  = driver.find_elements(By.CSS_SELECTOR, f'div.fastdeal-meta-container-outer.pad-right.{cabin}')
                    elif cabin == "suite" or cabin == "oceanview":
                        outer_div  = driver.find_elements(By.CSS_SELECTOR, f'div.fastdeal-meta-container-outer.pad-left.{cabin}')
                    try: # brochure price, our price, promo hilite(skip), you save
                        for div in outer_div:
                            try:
                                anchor = div.find_element(By.XPATH, './/a')
                                price = anchor.text
                                print(f'{cabin}:{price}')
                                extracted_price = extract_price(price)
                                hist = f"hist_{d}"
                                
                                if cabin not in eval(hist):
                                    eval(hist)[cabin] = []
                                    eval(hist)[cabin].append(extracted_price) # append brochure price
                                else: 
                                    if len(eval(hist)[cabin]) == 1: # append our price if we have stored brochure price
                                        eval(hist)[cabin].append(extracted_price)
                                    elif len(eval(hist)[cabin]) in [2,3]: # replace
                                        if did_brochure: #replace their price 
                                            # if eval(hist)[cabin][1] > extracted_price: #only when executing second fetch!
                                            body_prev_price = eval(hist)[cabin][1] #old price
                                            body_curr_price = extracted_price #just-fetched-price
                                            notify = True
                                            print(f'To notify? {notify}!!')

                                            #logic to send emails
                                            write_to_file(itinerary=itinerary, hist=hist, deal=d)  #only write the current deal
                                            # print("--- Sending email ... ---")
                                            subject = f"[NOT SPAM] Update on Deal #{body_deal}, {body_cabin}!"
                                            body = f"Deal #{body_deal} | {body_cabin}: {body_prev_price} --> {body_curr_price}\nPlease find the attached historical updates on all three deals."
                                            # send_email(sender_email, sender_password, recipient_email, subject, body, attachment_path)
                                            time.sleep(1)

                                            eval(hist)[cabin][1] = extracted_price 
                                            did_brochure = False
                                        else: # replace brochure first
                                            eval(hist)[cabin][0] = extracted_price
                                            did_brochure = True

                            except NoSuchElementException:
                                print(' get you-save %...')
                                try: 
                                    you_save_div = div.find_element(By.CSS_SELECTOR, 'div.fastdeal-meta-container-inner.you-save')
                                    you_save_span = you_save_div.find_element(By.CSS_SELECTOR, 'span.price-amount')
                                    pct = you_save_span.text
                                    extracted_pct = extract_number(pct)
                                    if len(eval(hist)[cabin]) != 3:
                                        eval(hist)[cabin].append(int(extracted_pct)) # append pct to the cabin list
                                    else:
                                        eval(hist)[cabin][2] = int(extracted_pct)
                                except NoSuchElementException:
                                    print(f"no you save is found, go to next div")
                    except NoSuchElementException:
                        print(f"NoSuchElementException, next div of four divs in total")
                
            except NoSuchElementException:
                print(f"NoSuchElementException, next deal")          
            print(f"hist_{d} looks like", eval(f"hist_{d}")) #one deal done, next deal

        driver.quit() #quit when all deals are fetched
        print("--- END in %s seconds ---" % (time.time() - start_time))
        # print(f"--- Going to sleep for {refresh_rate} seconds before doing another fetch... ---")
        time.sleep(refresh_rate) #go fetch data every 5 sec

