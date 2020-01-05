from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import os
import glob

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']
limit_loop = 5
def getFolder(service, folder_id="root"):
	
	print(folder_id)
	results = []
	page_token = None

	while True:
		# Call the Drive v3 API
		response = service.files().list(q="'"+ folder_id +"' in parents").execute()

		page_token = response.get('nextPageToken', None)
		items = response.get('files', [])

		if not items:
			break
		else:
			for item in items:
				results.append(item)

		if page_token is None:
			break

	return results

def main():

	creds = None

	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	service = build('drive', 'v3', credentials=creds)

	root = '1ywh1sPz_tv35htokvaHb-pS7-k8lXZbf'

	root_path = 'data/' + root
	
	all_data = {}
	if os.path.isdir(root_path):
		files = os.listdir(root_path)
		for file in files:
			with open(root_path + '/' + file, 'r') as f:
				data = json.loads(f.read())['data']

				all_data[file.split('.')[0]] = data


	queue_folder = []

	if bool(all_data):
		for (key,value) in all_data.items():
			for it in value:
				if it['id'] not in all_data and it['mimeType'] == 'application/vnd.google-apps.folder':
					queue_folder.append(it['id'])
	else:
		print('empty')
		queue_folder = [root]

	print(queue_folder)
	count = 0
	while len(queue_folder) > 0 or count > 500:
		new_queue_folder = []
		for folder_id in queue_folder:
			count += 1
			print(count)
			items = getFolder(service, folder_id)
			for item in items:
				print(item)
				print(item['mimeType'])
				if item['mimeType'] == 'application/vnd.google-apps.folder':
					new_queue_folder.append(item['id'])
			data_file = {
				'data': items
			}

			if not os.path.isdir(root_path):
				os.mkdir(root_path)
			with open(root_path + '/' + folder_id +'.json', 'w') as outfile:
				json.dump(data_file, outfile, indent=4, ensure_ascii=False)

		print(new_queue_folder)
		queue_folder = new_queue_folder
	
	print("Count: " + str(count))

if __name__ == '__main__':
	main()