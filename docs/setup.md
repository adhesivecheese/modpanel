# Setup Modpanel

Modpanel requires python3.6+. Required dependencies are listed in
`requirements.txt`. If you use pip, you may install dependencies by issuing 
`pip install -r requirements.txt` in the main Modpanel directory.
It is *strongly* recommended to do this inside a python virtual environment.

Once the requirements are installed, copy the default config file (located at 
`project/config.cfg.default`) to `project/config.cfg` and edit it to suit your
needs. 

## Basic Configuration
Change the `SECRET_KEY` to a long string or random bytes. This should not be 
changed again.

If you wish to store your user database in a different location, or use a more
robust database than sqlite3, modify the `SQLALCHEMY_DATABASE_URI` accordingly. 
There's generally no need to do this, and using a different database is out of 
scope for this documentation.

The logging section is set up with fairly sensible defaults, but if you're
tinkering with the code, you may wish to change the `LOG_LEVEL`, turn on 
`LOG_BACKTRACE`, or change the amount of time that Modpanel retains logs for 
before overwriting.

From here, Modpanel can be setup two ways: either for a single user as a 
personal use script, or for multiple users as a web app; this is configured by
setting `SINGLE_USER_MODE` to `True` or `False`


## Single-User Mode Setup

If setting up Modpanel for Single-User mode, `SINGLE_USER_MODE` should be set 
to `True` create a "script" type application on Reddit using 
[this link](https://www.reddit.com/prefs/apps/) (ensure you're logged into your 
correct moderator account before creating the app!).

You'll need to fill out the name field, and the redirect URI. The Redirect URI 
is not used, so feel free to use `http://localhost`, or any other valid URI.

You'll need two variables from the created app for your `config.cfg` file. The
line immediately below "personal use script" is your CLIENT_ID, and secret is 
your `CLIENT_SECRET`.

You will also need to fill in your username in the `REDDIT_USERNAME` field, and 
your Reddit password in the `REDDIT_PASSWORD` field.

When using Modpanel in Single-User Mode, there are no Modpanel accounts - 
anyone who knows your modpanel URL can moderate as you. As such, you should 
**not** make your server accessible from the internet, or leave it running when 
not using it.

## Multi-User Mode Setup

Multi-User mode uses OAuth2 to provide Reddit access to anyone who signs up 
through your instance of Modpanel. Create a "web app" type application on
Reddit using [this link](https://www.reddit.com/prefs/apps/). As with creating 
your application for Single-User Mode, the required fields are name and redirect 
URI; the difference here is that the redirect URI is actually used for 
authorization; this path will need to *exactly* match the URI that your instance 
will use to authenticate. For example, your server `example.com` might be serving
Modpanel on port `5000`; your redirect URI would be 
`http://example.com:5000/authorize_callback`. Please note that the protocol
portion of the path (`http://` or `https://`) *must* be included in this URI.

Using this example URI:

* `BASE_URL` would be `http://example.com`
* `SERVER_PORT` would be `5000`
* `AUTHORIZATION_PATH` would be `authorize_callback`

Set `NEW_ACCOUNTS_ACTIVE` to `True` to enable all newly created accounts to 
immediately use Modpanel, or to `False` to require an instance admin to 
activate the account before usage.

### First Run

On the first run of Modpanel, you'll be redirected to the signup page; the 
first account to sign up is automatically marked as active and made an 
administrator for your instance.


## Running Modpanel

As Modpanel is a WSGI application, there are a number of ways to run it. If 
you're Running in Single-User Mode, the Flask development server may be fine;
you can run Modpanel by issuing `flask --app project/__init__.py run` from the 
Modpanel root directory.

If your instance is intended to be used by multiple users, you'll almost 
certainly want a more robust server to run your application; a startup script 
(`start.sh`) is included which uses gunicorn and gevent (which may be installed
through pip by running `pip install gunicorn gevent`).

Modpanel *should* run fine through Apache or nginx's WSGI modules; setup for 
those are beyond the scope of this documentation.