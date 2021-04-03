from PIL import Image, ImageTk
from io import BytesIO
import json
import os
import requests
import time
import tkinter as tk
import tkinter.ttk as ttk
import webbrowser


# Save (unix) time at program start.
time0 = time.time()
github_user = 'Vianpyro'
github_api_url = 'https://api.github.com'


def retrieve_online_json(url:str) -> dict:
    """
    This function downloads an online json file and returns it.
    
    :argument url:  The url where to find the json file to retrieve.
    :return:        A dictionary containing all the downloaded data.
    """
    return requests.get(url).json()


# If the save.json file exists open it else create it.
if __name__ == '__main__' and os.path.exists('save.json'):
    with open('save.json', 'r') as json_file:
        json_data = json.load(json_file)

    # If the file is not empty, read its data else raise an error.
    if len(json_data):
        # If the data was updated less than 10 minutes ago use it else update it.
        if json_data['last_update'] + 600 < time0:
            print(f'Updating ({(time0 - json_data["last_update"]) / 60:.2f} minutes) old data...')
            json_data['last_update'] = time0
            
            # Load the github user's data.
            try:
                github_user_json = retrieve_online_json(f'{github_api_url}/users/{github_user}')
            except Exception:
                raise ValueError(Exception)
            
            if "message" in github_user_json:
                raise ValueError("Invalid url, please check it is correct before sending the request.")
            else:
                print(f"Successfuly loaded {github_user}'s data.")
                
                github_repos_json = retrieve_online_json(github_user_json['repos_url'])
                
                # Update the json data.
                json_data['data']['user'] = github_user_json
                json_data['data']['repos'] = github_repos_json
            
            # Update the data in the json file.
            with open('save.json', 'w') as json_file:
                json.dump(json_data, json_file, indent = 4, sort_keys = True)
        else:
            print(f'Using ({(time0 - json_data["last_update"]) / 60:.2f} minutes) old data...')
    else:
        raise ValueError('Empty save, please delete the file and re-run the program.')
else:
    with open('save.json', 'w') as json_file:
        json.dump({"last_update": 0, "data": {}}, json_file)
    raise ValueError('No save file found, please re-run the program.')


############################
# LAUNCHER
############################
class Window(tk.Frame):
    def __init__(self, master=None, widgets_list: list = []):
        super().__init__(master)
        self.pack()
        self.create_widgets(widgets_list)
        self.master.title('Vianpyro')

    def create_widgets(self, widgets_list: list = []) -> None:
        # Icon.
        raw_image = requests.get(json_data['data']['user']['avatar_url'])
        image_data = raw_image.content
        image = ImageTk.PhotoImage(Image.open(BytesIO(image_data)))
        panel = tk.Label(self, image = image)
        panel.photo = image
        panel.pack()

        # Repos.
        repos = [ttk.Button(self) for widget in widgets_list]
        for i in range(len(repos)):
            repos[i]["text"] = widgets_list[i][0].upper() + widgets_list[i][1:].replace('_', ' ')
            repos[i]["cursor"] = 'circle'
            repos[i]["command"] = lambda: webbrowser.open(f'https://{github_user.lower()}.github.io/{widgets_list[i]}/')
            padding_y = [5, 5]
            if i == 0:
                padding_y[0] *= 3
            elif i == len(repos) - 1:
                padding_y[1] *= 3

            repos[i].pack(padx = (15, 15), pady = padding_y)

if __name__ == '__main__':
    root = tk.Tk()
    app = Window(
        master = root,
        widgets_list = [
            repo['name'] for repo in json_data['data']['repos']
        ])
    app.mainloop()
