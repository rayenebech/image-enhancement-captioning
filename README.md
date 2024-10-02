# Installing the app
```
python3 -m venv mvenv
source mvenv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

# Running the app
```
streamlit run app.py
```

If you are running the app in a cloud environement make sure to create a tunel to access the streamlit app:
```
npx localtunnel —-port 8501
```

Then paste the puplic url (without the port number) into the passcode requested.


# UI Examples

The user can enter an intial descirption and upload a picture:
![input area](assets/input.png)

Then the enhanced image and a descriptionn is generated:

![output area](assets/output.png)