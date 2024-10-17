import sys
import requests
import os
import concurrent.futures

usrname = "placeholder"
psw = "placeholder"
nextcloud = "placeholder"
backups="placeholder"

if usrname == "placeholder" : 
    print("replace all placeholders into main.py") 
    exit(1)

def create_folder(path):
    path = path.replace(" ", "_")
    url = f'{nextcloud}/{path}'
    print(f"creating folder {path}")
    requests.request('MKCOL', url, auth=(usrname, psw))

def send_file(filepath, folderpath):
    folderpath=folderpath.replace(" ", "_")
    cmd = f'curl -u {usrname}:{psw} -T "{filepath}" "{nextcloud}/{folderpath}" '
    
    url = f"{nextcloud}/{folderpath}"
    print(f"sending file {filepath}")
    with open(filepath, 'rb') as file:
        requests.put(url, data=file, auth=(usrname, psw))
    

create_folder(backups)    

folders_to_create=[]
files_to_send_fpath=[]
files_to_send_url=[]

i=1
while i < sys.argv.__len__():
    path = sys.argv[i].rstrip("/")
    rootdir, fold =os.path.split(path)
    for root, dirs, files in os.walk(path):
        if("." not in root.lstrip(rootdir)):
            folders_to_create.append(backups+"/"+root.lstrip(rootdir))
            for file in files:
                files_to_send_fpath.append(root+"/"+file)
                files_to_send_url.append(backups+"/"+root.lstrip(rootdir)+"/"+file)
    i=i+1

for fold in folders_to_create:
    create_folder(fold)

#for fp, fu in zip(files_to_send_fpath, files_to_send_url):
#    send_file(fp, fu)
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Submit tasks for sending files to the executor
    futures = [executor.submit(send_file, fp, fu) for fp, fu in zip(files_to_send_fpath, files_to_send_url)]
    
    # Optionally wait for all futures to complete
    for future in concurrent.futures.as_completed(futures):
        # You can handle exceptions here if needed
        try:
            future.result()  # This will raise an exception if the send_file call failed
        except Exception as e:
            print(f'Error sending file: {e}')