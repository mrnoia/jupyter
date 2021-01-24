def month_string_to_number(string):
    m = {
        'jan':'01',
        'feb':'02',
        'mar':'03',
        'apr':'04',
        'may':'05',
        'jun':'06',
        'jul':'07',
        'aug':'08',
        'sep':'09',
        'oct':'10',
        'nov':'11',
        'dec':'12'
        }
    s = string.strip()[:3].lower()
    try:
        out = m[s]
        return out
    except:
        return ''
        
def get_page_source(page_url):        
    from selenium import webdriver      
    #webdriver_path = r'/usr/bin/chromedriver' #linux
    webdriver_path = r'C:\Users\admin\Documents\chromedriver\chromedriver.exe' #windows   
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument("--headless")
    chromeOptions.add_argument("--remote-debugging-port=9222")
    chromeOptions.add_argument('--no-sandbox')   
    browser = webdriver.Chrome(webdriver_path, options=chromeOptions)
    browser.get(page_url)
    # get page source code
    return browser.page_source

def get_league_matches(league_id,future_matches_url,time_flag):    
    from bs4 import BeautifulSoup
    from datetime import datetime, timedelta
    words=future_matches_url.split("/")
    country=words[4]
    league=words[5]
    page_source = get_page_source(future_matches_url)
    soup = BeautifulSoup(page_source, 'html.parser')
    fixres_body = soup.findAll('table', {'id': 'tournamentTable'})
    soup1 = BeautifulSoup(str(fixres_body), 'html.parser')
    tags=soup1.findAll()
    i=1
    odd_list=[]
    odd1=''
    odd1r=0
    odd1p=0
    oddx=''
    oddxr=0
    oddxp=0
    odd2=''
    odd2r=0
    odd2p=0                   
    oddtp=0
    maxoddp=0
    maxoddout=0
    for tag in tags: 

        if tag.get('class') is not None:

            if 'datet' in tag.get('class') and 'table-time' not in tag.get('class'):                
                today=datetime.now()
                yesterday = today- timedelta(days=1)
                tomorrow = today + timedelta(days=1)
                
                match_date=tag.text.strip()
                match_day=match_date[0:2] 
                match_month=month_string_to_number(match_date[3:6])
                match_year=match_date[7:11] 
                match_date1=match_year +'-'+match_month +'-' + match_day
                
                if match_date.find('Today')==0:
                    match_date1 = today.strftime("%Y-%m-%d")
                if match_date.find('Yesterday')==0:
                    match_date1 = yesterday.strftime("%Y-%m-%d")
                if match_date.find('Tomorrow')==0:
                    match_date1 = tomorrow.strftime("%Y-%m-%d")
                match_date=match_date1

            if  'table-time' in tag.get('class'):
                match_time=tag.text.strip().replace("'", "") 

            if  'table-participant' in tag.get('class'):
                match_participant=tag.text.strip()
                h_team=match_participant.split(' - ')[0]
                a_team=match_participant.split(' - ')[1]
            
            if time_flag=='past':                
                if  'table-score' in tag.get('class'):                
                    match_score=tag.text.strip()
                    h_goals=match_score.split(':')[0]
                    a_goals=match_score.split(':')[1]

            if  'odds-nowrp' in tag.get('class'):
                if i== 1:
                    odd1= tag.text.strip()
                    if odd1.find('/')>-1:
                        odd1num=int(odd1.split('/')[0])
                        odd1den=int(odd1.split('/')[1])
                        odd1r=odd1num/odd1den
                        odd1p=odd1den/(odd1num+odd1den)
                if i== 2:
                    oddx= tag.text.strip()
                    if oddx.find('/')>-1:
                        oddxnum=int(oddx.split('/')[0])
                        oddxden=int(oddx.split('/')[1])
                        oddxr=oddxnum/oddxden
                        oddxp=oddxden/(oddxnum+oddxden)
                if i== 3:
                    odd2= tag.text.strip()
                    if odd2.find('/')>-1:
                        odd2num=int(odd2.split('/')[0])
                        odd2den=int(odd2.split('/')[1])
                        odd2r=odd2num/odd2den
                        odd2p=odd2den/(odd2num+odd2den)
                        oddtp=odd1p+oddxp+odd2p
                        maxoddp=max(odd1p,oddxp,odd2p)
                        if maxoddp==odd1p:maxoddout=1
                        if maxoddp==oddxp:maxoddout=0
                        if maxoddp==odd2p:maxoddout=2

                    match_dict = {}                
                    for variable in [
                        "league_id",
                        "country",
                        "league",                        
                        "match_date",                       
                        "match_time",
                        "match_participant",
                        "h_team",
                        "a_team",                    
                        "odd1",
                        "odd1r",
                        "odd1p",
                        "oddx",
                        "oddxr",
                        "oddxp",
                        "odd2",
                        "odd2r",
                        "odd2p",                   
                        "oddtp",
                        "maxoddp",
                        "maxoddout"                   
                       
                    ]:
                        match_dict[variable] = eval(variable)                
                    odd_list.append(match_dict)                
                i = [1,i+1][i<3]        
    return odd_list

def run_mysql_sql(sql, action, hostname, username, password, database):
    import mysql.connector
    try:
        mySqlConnection = mysql.connector.connect(
            host=hostname, user=username, passwd=password, db=database, connect_timeout=1000)
        mysqlcursor = mySqlConnection.cursor()
        mysqlcursor.execute(sql)
        if action == 's':
            result = mysqlcursor.fetchall()
            mySqlConnection.commit()
            mySqlConnection.close()
            return result
        else:
            mySqlConnection.commit()
            mySqlConnection.close()
            return 0
    except:
        return -1