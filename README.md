# Smallcap-SIP-BOT (Backend)

## Overview

Hi! **Smallcap-SIP-BOT** is a tool designed to help you automate your investment actions, especially with regards to **Smallcap Fund** Investments.

Smallcap Funds are highly volatile and usually considered risky, but one can take full advantage of this volatility to increase returns by taking some actions with respect to the market movement. [This video](https://www.youtube.com/watch?v=ppxnjQ86T-Q) can help you understand the concept better.

Since the goal of this kind of approach is to increase returns with the help of volatility, the investor must make necessary moves based on the market movements. But this is a tedious task as it involves keeping an eye on the valuations constantly to make the next move, which is why the **Smallcap-SIP-BOT** is here.

**Smallcap-SIP-BOT** fetches the daily ending values, computes the required valuations, and makes a final decision if there is any action required from the user to maximize their returns. If it finds one, it will immediately alert the subscriber via e-mail according to the preferences they set.

## Tools used

- **Django** [Core Backend Functionality]
- **Django REST** [RESTFul APIs]
- **MongoDB** [NoSQL Database]
- **YAML** [Configuration Files]

## Installation Steps

1.  Pull the entire repository to your local machine `git pull origin main`
2.  Create a Python virtual environment in the main directory `python -m venv venv`
3.  Activate your newly created Python virtual environment `venv\Scripts\activate`
4.  Install all the required packages for the project present in the requirements.txt file `pip install -r requirements.txt`
5.  Download, Install and set-up MongoDB from their [official website](https://www.mongodb.com/)
6.  You will have to set three environment variables in your system which the script will access.
    **MAIL_ID**: This is the email account the service uses to alert subscribers.
    **MAIL_PASSWORD**: This is the password for the above mentioned email account.
    **SECRET_KEY**: This is the secret key Django uses for cryptographic signing. Follow [these instructions](https://www.educative.io/answers/how-to-generate-a-django-secretkey) to generate a new secret key and update it to this environment variable.
7.  Open the **config.yml** file inside **services directory**, set the mode to `initialization`and run the services file using `python services.py`. This will seed up the database collections with initial data. Once it is done, change the mode back to `production`
8.  Schedule your **service** to run once a day preferably after 6 PM IST.
9.  You can clear up the data in all the collections, by running `python clear_tables.py`

## Credits

Thanks to [Mr. Shankar Nath](https://www.youtube.com/@shankarnath) for explaining this concept in his [video here](https://www.youtube.com/watch?v=ppxnjQ86T-Q) which inspired me to come up with an automated approach to this amazing idea.
