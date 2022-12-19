# Accounts and Permissions

## Modpanel Accounts

If not using [Single User Mode](setup.md#single-user-mode-setup), all users 
must create an account with Modpanel. Your Modpanel username nor password need 
to match your Reddit account or password; the Modpanel account is simply a 
convenience to save your authorization from Reddit, as well as to allow any 
Modpanel Administrators on your instance to make you an Administrator, or to 
activate or deactivate your Modpanel account.

**Your Modpanel account credentials do *not* need to match your Reddit credentials.**


## OAuth Scopes - what permissions Modpanel Requests 

Due to the way Reddit's API is scoped, Modpanel needs a fairly long list of 
account permissions when connecting to Reddit. Here's a rundown of what 
Modpanel requests, and why it needs it:

* [identity](https://www.reddit.com/dev/api/oauth/#scope_identity)
	* `Access my reddit username and signup date`
	* Modpanel needs this to view your eddit username, which is needed for 
	leaving toolbox notes.

* [modposts](https://www.reddit.com/dev/api/oauth/#scope_modposts)
	* `Approve, remove, mark nsfw, and distinguish content in subreddits I moderate`
	* This permission is what grants Modpanel access to core moderation features.

* [modlog](https://www.reddit.com/dev/api/oauth/#scope_modlog)
	* `Access the moderation log in subreddits I moderate`
	* Modpanel queries the modlog for a subreddit when a queue is open to 
	determine who else is actioning things, and to confirm that your actions 
	have processed through to Reddit.

* [wikiedit](https://www.reddit.com/dev/api/oauth/#scope_wikiedit)
	* `Edit wiki pages on my behalf`
	* Toolbox notes and Modpanel Settings are both stored as subreddit wikipages;
	this permission enables you to leave usernotes and save Modpanel settings.

* [wikiread](https://www.reddit.com/dev/api/oauth/#scope_wikiread)
	* `Read wiki pages through my account`
	* the flip side of wikiedit, this allows Modpanel to read Usernotes and 
	Modpanel Settings from Reddit's wiki pages.

* [modcontributors](https://www.reddit.com/dev/api/oauth/#scope_modcontributors):
	* `Add/remove users to approved user lists and ban/unban or mute/unmute users from subreddits I moderate.`
	* Needed to allow you to issue bans through Modpanel.

* [modmail](https://www.reddit.com/dev/api/oauth/#scope_modmail)
	* `Access and manage modmail via mod.reddit.com`
	* Needed to send modmail to users if your subreddit sends removal messages 
	via modmail.

* [read](https://www.reddit.com/dev/api/oauth/#scope_read)
	* `Access posts and comments through my account`
	* This scope allows Modpanel to read posts and comments for a selected queue.

* [history](https://www.reddit.com/dev/api/oauth/#scope_history)
	* `Access my voting history and comments or submissions I've saved or hidden`
	* Here, Reddit's description of this scope is only telling half the story. 
	Modpanel doesn't need to see *your* voting history, or things you've saved 
	or hidden; this permission is required to view *any* user's history, not 
	just your own. Viewing history is needed for Wiping History during a ban, 
	or for viewing a user page through Modpanel

* [report](https://www.reddit.com/dev/api/oauth/#scope_report)
	* `Report content for rules violations. Hide & show individual submissions` 
	* The only permission which Modpanel Requests but doesn't currently use. 
	The intent is to add a report button to queue items to enable you to report 
	contnet you're not sure about how to moderate.