import pickle
from googleapiclient.discovery import build

try:
    with open("Agribot/token.pickle", "rb") as token:
        creds = pickle.load(token)
    service = build("drive", "v3", credentials=creds)
    query = "name = 'Agribotimage' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    folders = results.get("files", [])
    if folders:
        print("FOLDER_ID:", folders[0]["id"])
    else:
        print("NOT_FOUND")
except Exception as e:
    print("FAILED:", e)
