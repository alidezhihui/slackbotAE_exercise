from os import getenv
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
import slack_sdk
import dotenv
from flask import Flask, request, jsonify
from slackeventsapi import SlackEventAdapter
from slack_bolt.adapter.flask import SlackRequestHandler
import requests
import json

payload_create = [
	{
		"type": "section",
		"text": {
			"type": "mrkdwn",
			"text": "Hello, I can assist with scheduling for your group. If you need to set up a meeting click *create*.",
		},
	},
	{"type": "divider"},
	{
		"type": "actions",
		"elements": [
			{
				"type": "button",
				"text": {"type": "plain_text", "text": "Create", "emoji": True},
				"value": "create",
				"action_id": "create",
			}
		],
	},
]


payload_weather = {
	"type": "modal",
	"title": {
		"type": "plain_text",
		"text": "My App",
		"emoji": True
	},
	"submit": {
		"type": "plain_text",
		"text": "Submit",
		"emoji": True
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel",
		"emoji": True
	},
	"blocks": [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Type Your Location",
				"emoji": True
			}
		},
		{
			"type": "rich_text",
			"elements": [
				{
					"type": "rich_text_section",
					"elements": [
						{
							"type": "text",
							"text": "Basic bullet list with rich elements\n"
						}
					]
				},
				{
					"type": "rich_text_list",
					"style": "bullet",
					"elements": [
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "item 1: "
								},
								{
									"type": "emoji",
									"name": "basketball"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "item 2: "
								},
								{
									"type": "text",
									"text": "this is a list item"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "item 3: "
								},
								{
									"type": "link",
									"url": "https://slack.com/",
									"text": "with a link",
									"style": {
										"bold": True
									}
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "item 4: "
								},
								{
									"type": "text",
									"text": "we are near the end"
								}
							]
						},
						{
							"type": "rich_text_section",
							"elements": [
								{
									"type": "text",
									"text": "item 5: "
								},
								{
									"type": "text",
									"text": "this is the end"
								}
							]
						}
					]
				}
			]
		},
		{
			"dispatch_action": True,
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "plain_text_input-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Label",
				"emoji": True
			}
		}
	]
}

def get_weather_data(city, state):
	with open("./city.list.json", "r") as file:
		us_cities_data = json.load(file)
	city_data = [uscities for uscities in us_cities_data if uscities["country"] == "US" and uscities["name"] == city and uscities["state"] == state]
	return city_data[0]
	
def get_weather_details_str(data, detail, city, state):
	details_str = ""
	if detail == "temperature":
		temp_now = data["main"]["temp"]
		temp_min = data["main"]["temp_min"]
		temp_max = data["main"]["temp_max"]
		details_str = f"The temperature at {city}, {state} right now is {temp_now}. The max temp is {temp_max}, and the min temp is {temp_min}!"
	elif detail == "humidity":
		humidity = data["main"]["humidity"]
		details_str = f"The humidity at {city}, {state} right now is {humidity}!"
	elif detail == "wind":
		wind_speed = data["wind"]["speed"]
		wind_deg = data["wind"]["deg"]
		wind_gust = data["wind"]["gust"]
		details_str = f"The wind speed at {city}, {state} right now is {wind_speed}!"
	elif detail == "sunTime":
		sunrise = data["sys"][sunrise]
		sunset = data["sys"][sunset]
	elif detail == "weather":
		type = data["weather"]["main"]
		description = data["weather"]["description"]
		details_str = f"The weather at {city}, {state} is {type}: {description}!"
	
	return details_str




dotenv.load_dotenv()

print(f"this is my token {getenv('SLACK_BOT_TOKEN')}")

client = slack_sdk.WebClient(token=getenv('SLACK_BOT_TOKEN'))

slack_app = App(token=getenv('SLACK_BOT_TOKEN'),
		  signing_secret=getenv('SLACK_SIGNING_SECRET'),
		  raise_error_for_unhandled_request=True
		  )
slack_handler = SlackRequestHandler(slack_app)
app = Flask(__name__)



@slack_app.message("Hello")
def respond_to_hello(message, say):
	user = message["user"]
	say("Hello" + str(user))


@app.route("/cmd/get_weather", methods=["POST"])
def get_weater():
	payload = request.form.get("payload")
	headers = request.headers
	apikey = getenv('OPENWEATHER_API_KEY')

	# Process the Slack request using Slack Bolt
	command = request.form.get("command")
	text = request.form.get("text")
	user_id = request.form.get("user_id")
	channel_id = request.form.get("channel_id")

	# Process the command and generate a response
	response_text = (
		f"You invoked the '{command}' command with text '{text}' as user '{user_id}'.")
	
	# ask users to provide the city and state for which they would like to receive weather info
	city = "Santa Cruz"
	state = "CA"
	weather_detail = ""
	# get the lat and lon of users' specified city and state
	# 1. Read the JSON file
	city_loc = get_weather_data(city, state)
	city_lon = city_loc[0]["coord"]["lon"]
	city_lat = city_loc[0]["coord"]["lat"]


	url = f"https://api.openweathermap.org/data/2.5/weather?lat={city_lat}&lon={city_lon}&appid={apikey}"
	weather_data = requests.get(url).json()
	
	detail_str = get_weather_details_str(weather_data, weather_detail, city, state)
	client.chat_postMessage(channel=channel_id, text=f'api key: {apikey}, \n {response}')
	temp_in_kelvin = response['main']['temp']
	temp_in_fahrenheit = kelvin_to_celsius_fahrenheit(temp_in_kelvin)['fahrenheit']

	client.chat_postMessage(channel=channel_id, text=f'Hello Command!')

	# Send the response back to Slack
	return "", 200



######################## Bot Events ###################
# Define a route for your Slack Bolt events
@app.route("/slack/events", methods=["POST"])
def slack_events():
	# Retrieve and process incoming Slack events using the Slack Bolt app
	print("receive an event!!")
	request_data = request.get_json()
	
	if request_data.get('type') == 'url_verification':
		print("url verification")
		return jsonify({'challenge': request_data['challenge']})
	# Process the Slack request using SlackRequestHandler
	response = slack_handler.handle(request)

	return "", 200

# This will match any message that contains 👋
@slack_app.message("weather app")
def say_hello(message, say):
	user = message['user']
	usage = \
	' Here are the usage of the weather map: \n  \
	use slash command \\weatherAPP get \n Then click the button GET, a panel will show up \n Provide your city name and Select the kind of weather information ur interested, then Click Submit Button \
	\n Enjoy!' 
	say(f"Hi there, <@{user}>! {usage}")

## Helper function
def kelvin_to_celsius_fahrenheit(kelvin):
	celsius = kelvin - 273.15
	fahrenheit = celsius * (9/5) + 32
	return {'celsius': celsius, 'fahrenheit': fahrenheit}

if __name__ == "__main__":
	app.run(debug=True, port=5002)

# `

# handler = SlackRequestHandler(app)

app = Flask(__name__)

# # Define a route for your Slack Bolt events
# @app.route("/slack/events", methods=["POST"])
# def slack_events():
#     # Retrieve and process incoming Slack events using the Slack Bolt app
#     request_data = request.get_json()
	
#     if request_data.get('type') == 'url_verification':
#         print("url verification")
#         return jsonify({'challenge': request_data['challenge']})
#     # Process the Slack request using SlackRequestHandler
#     response = slack_handler.handle(request)

#     return "", 200