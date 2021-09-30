### SlackUp

Backup slack messages.

### Prerequisites

Install slack SDK
```
pip install slack_sdk
pip install requests
```
You need to get a user token for the Slack API. For this you need to create a slack App, which is straightforward to do: https://api.slack.com/apps. Create an App selecting the desired workspace. 

Go to "OAuth & Permissions", scroll down to "User Token Scopes", and add the following scopes:
![image](https://user-images.githubusercontent.com/751875/135373138-dbf2f67f-91a7-4e0b-8d75-9b80bea448be.png)

Then install the app on your workspace (via Install App option).


### Usage

Clone repository and cd into it
```
git clone https://github.com/webglider/slackup.git
cd slackup
```

Set slack API token environment variable (replace the below with your token)
```
export SLACK_TOKEN=xoxp-blabla-blabla-blabla-blabla
```

Create a directory for history
```
mkdir history
```

Run the script
```
python slackup.py
```

Conversation history will be fetched via the Slack API and dumped into pickle files in `history/`

