### SlackUp

Backup slack messages.

Install slack SDK
```
pip install slack_sdk
```

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

