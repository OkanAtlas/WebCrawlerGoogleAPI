import base64                                                                #Package to encode and decode byte messages
from email.mime.multipart import MIMEMultipart                                     #Package to create multipart messages
from email.mime.text import MIMEText                                                    #Package to create text messages

import requests                                                         #Package to make html content requests to an URL
import pandas as pd                                                                    #Package to work with data frames
import pickle                                                                              #Package to serialize objects
from googleapiclient.discovery import build                                                #Package to build API service
from googleapiclient.http import MediaFileUpload                           #Package to allow file upload to Google Drive
from google_auth_oauthlib.flow import InstalledAppFlow                                 #Package to authorize the Web App

from lxml import html                                                                        #Package to parse HTML code

# Set API and authentication information
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://mail.google.com/',
          'https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.compose',
          'https://www.googleapis.com/auth/gmail.send']

KEY_FILE = './data/keys.json'
API_NAME = 'drive'
API_NAME_2 = 'gmail'
API_VERSION = 'v3'
API_VERSION_2 = 'v1'

credentials = None
pickle_file = f'token_{API_NAME}_{API_VERSION}.pickle'

flow = InstalledAppFlow.from_client_secrets_file(KEY_FILE, SCOPES)
credentials = flow.run_local_server()

with open(pickle_file, 'wb') as token:
    pickle.dump(credentials, token)

# Build Google Drive API service
googleC = build(API_NAME, API_VERSION, credentials=credentials)

#Build Gmail API service
gmailC = build(API_NAME_2, API_VERSION_2, credentials=credentials)

productDataList = []


def CrawlToWeb(pageUrl):
    page = requests.get(pageUrl)  # request the web page's html content as a string
    tree = html.fromstring(page.content)  # parse the html string to create a html tree

    brandName = tree.xpath('//*[@id="product-name"]/span/a/text()')

    if len(brandName) == 0:                                                                   #if there is no brand name
        return                                                                                   #its not a product page

    # scrap needed information from the html tree by using the xPaths of the content
    productName = tree.xpath('//*[@id="product-name"]/text()')
    productPrice = tree.xpath('//*[@id="productRight"]/div/div[2]/div[1]/div/div/span/span/text()')
    productAvailability = tree.xpath('//*[@id="productRight"]/div/div[4]/div[2]/div[2]/div/text()')
    productCode = tree.xpath('//*[@id="productRight"]/div/div[6]/div[2]/text()')

    totalChoices = len(productAvailability) - 1
    unavailableProductCount = 0

    # Detect the unavailable product types through the @class match
    for i in range(totalChoices):
        typeClass = tree.xpath('//*[@id="productRight"]/div/div[4]/div[2]/div[2]/div/a[' + str(i + 1) + ']/@class')
        if typeClass[0] == 'col box-border passive':
            unavailableProductCount += 1

    # Create append values to prevent indexing errors
    if len(productPrice) == 0:
        productPriceText = "-"
    else:
        productPriceText = productPrice[0] + "TL"

    if len(productCode) >= 2:
        productCodeAppend = productCode[0].strip() + productCode[1].strip()
    else:
        productCodeAppend = "-"

    if len(productName) >= 2:
        productNameAppend = productName[1].strip()
    else:
        productNameAppend = "-"

    if totalChoices > 0:
        productAvailabilityAppend = ((totalChoices - unavailableProductCount) / totalChoices) * 100
    else:
        productAvailabilityAppend = "0"

    # Append the scraped data to list
    productDataList.append([pageUrl, productCodeAppend, productNameAppend, productAvailabilityAppend, productPriceText])


# MAIN FUNCTION
def main():
    urlHeader = "https://www.markastok.com"

    # Read the Excel file to a data frame
    urlTails = pd.read_excel(r".\data\URL's.xlsx")

    # Cycle through every URL in the data frame file
    for i in range(len(urlTails)):
        CrawlToWeb(urlHeader + str(urlTails.iloc[i].item()))                          # Call to the web crawler function
        print(str(i + 1) + " pages visited out of " + str(len(urlTails)) + " pages.")

    # Initialize a data frame with set column names and transfer the data in the list
    productDataFrame = pd.DataFrame(productDataList,
                                    columns=['URL', 'SKU', 'Product Name', 'Availability', 'Sale Price'])
    productDataFrame = productDataFrame.sort_values(by=['Availability'], ascending=False)  # Sort by availability

    write2Excel = pd.ExcelWriter('./data/output.xlsx')  # Initialize Excel Writer
    productDataFrame.to_excel(write2Excel)  # Write data frame to Excel file with the initialized writer
    write2Excel.save()  # Save the Excel file

    googleDriveFileName = 'Markastok | Ürünraporu'
    punct = "'"

    # Create metadata for the Google Drive upload
    file_metadata = {
        'name': googleDriveFileName
    }

    # Select the upload file and set the file type
    media_content = MediaFileUpload('./data/output.xlsx',
                                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # Create a new file to Google Drive with the created metadata and content
    file = googleC.files().create(
        body=file_metadata,
        media_body=media_content
    ).execute()

    query = "name= {}{}{}" .format(punct, googleDriveFileName, punct)

    driveFiles = googleC.files().list(q=query,
                                      orderBy='createdTime').execute()

    # Get the id of the latest created file with the specified name
    fileSeries =   driveFiles.get('files', [])
    createdDriveFileId = fileSeries[len(fileSeries) - 1].get('id')

    #Create file permission request body
    requestBody = {
        'role': 'reader',                                                       #Link only allow people to read the file
        'type': 'anyone'                                                     #Anyone with the link can accessed the file
    }

    #Execute file permission settings to the file with the specified file id
    googleC.permissions().create(
        fileId=createdDriveFileId,
        body=requestBody
    ).execute()

    #Retrieve web sharing link of the file by using the file id
    shareLinkResponse = googleC.files().get(
        fileId=createdDriveFileId,
        fields='webViewLink'
    ).execute()

    #Extract the link from the response as a string
    fileURL = shareLinkResponse.get('webViewLink')

    #Set mailing information
    mailTo = 'people@analyticahouse.com'
    mailSubject = 'Okan Karakas - Software Developer Case Results'

    #Buil mail message
    message = MIMEMultipart()
    message['to'] = mailTo
    message['subject'] = mailSubject
    message.attach(MIMEText(fileURL, 'plain'))
    raw_msg = base64.urlsafe_b64encode(message.as_bytes()).decode()

    #Send the mail from the authenticated user
    gmailC.users().messages().send(userId='me', body={'raw': raw_msg}).execute()

main()  # Call to main function
