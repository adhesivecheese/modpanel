# Parts of Modpanel

## The Header
The header appears on most pages, and will contain relevant links for the page 
you're currently on. A few standard items will always appear in the header. 

### The Left Hand Side

* `Modpanel`, which will take you to the [main page](pages.md#main-page) which 
contains the list of subreddits you moderate. On a subreddit queue page, a 
badge will appear to the top right indicating the number of currently-loaded 
unactioned items.
* `Modmail` is a link which will take you to modmail on Reddit.

Additionally, if you're an administrator for your instance of Modpanel, the 
`Administration` page will be linked here.

All links except `Modpanel` will be collapsed into the right-hand hamburger 
menu on small screens/mobile.

If you're on a [queue page](pages.md#queue-page), `Administration` will 
disappear, and be replaced with links to different queues: `Modqueue`, `Hot`, 
`Rising`, and `New`.

These options are collapsed into a hamburger menu on small screens and mobile 
devices.

### The Right Hand Side

* `About` displays an about page; here you can find the version number as well 
as links for more information about Modpanel.
* Your Modpanel username. This has a drop-down menu allowing you to change the 
theme for modpanel on your current device.
* `Logout` - log out of Modpanel.

If you're on a [subreddit page](pages.md#queue-page), an additional item, 
`Subreddit Settings`, will appear to manage Modpanel settings for your 
subreddit.


## Main Page

The main page of Modpanel will provide you with a list of subreddits you 
moderate, and the number of queue items for each subreddit. If you're not logged
in (and not in [Single-User Mode](setup.md#single-user-mode-setup)), you'll be 
redirected to the login page.


## Queue Pages

When on a Queue page, The Modpanel link in the header will have a badge in the 
top right corner indicating the number of unactioned items in your 
currently-loaded queue; this number live-updates as actions are performed by 
you or others.

Queue pages have two columns; the left column (which is hidden on
mobile) contains information and navigation, and the larger right column is a 
stream of posts in your currently loaded queue.

### The Left Column
The left column contains four sections.

* Recently Active Moderators - this will show you all moderators who have 
performed a mod action on Reddit within the last 15 minutes. This information 
is pulled from your subreddit's modlog, not through Modpanel itself, so even 
if your teammate isn't using Modpanel, they'll still show as active. This 
updates once every 60 seconds, or whenever a mod performs an action. Mousing 
over the relative time will give you an exact timestamp of when the action 
took place.

* Items with User Reports - A list of post titles/comments in your 
currently-loaded queue which have been reported by users. Clicking on a title 
will jump you to that item in the right column.
* Items with Mod Reports - The same thing as with User reports, but for items 
reported by your moderators (not AutoModerator)
* Highlighted Word Count - Shows the word count of your currently-selected 
text. This is a quick-and-dirty crude estimation based on the number of breaks 
between characters, so there may be a small amount of variance from reality.

### The Right Column
The right column contains a list of items on your currently loaded queue, each 
in it's own panel. The title is a link to the item on Reddit. The arrow on the 
top right of each panel allows you to collapse that panel.

The relative time for the post updates once a minute or when a moderator action 
is registered, just like the times for Recently Active Moderators; mousing over 
the timestamp allows you to view the exact time the post was made.

Clicking on the username will take you to their profile page on Reddit; 
clicking the overview button next to their name will take you to their Modpanel 
[user page](pages.md#user-page).

Below this, you'll find three tabs:

* Reports - shows you a list of reports, if any, for the current item. If 
Modpanel detects a valid link in a report, it will turn it into a hyperlink 
allowing you to easily access it without needing to copy and paste.
* Toolbox Notes - Will be badged to the top right with the number of usernotes 
a user has, whether this tab is active or not. Clicking on this tab will display 
current notes, and allow you to add a note to the user. **Please Note:** the 
note count does not currently update when a note is left while the page is 
loaded, or if you leave a note. Notes may not currently be deleted through this 
interface.
* Ban - A mechanism to permanently ban a user; more detail can be found in 
[Moderating](queue.md#bans)

Below these tabs will be the body of the post (**Please Note:** image posts are 
not currently supported). Modpanel will insert RES-style expand-image buttons 
for imgur links and any url that ends with `jpg` or `png`. Modpanel renders 
text *almost* identically to Reddit, with one opinionated exception: Code blocks
which are too wide for the panel will wrap instead of scroll horizontally.

On queue pages other than modqueue, which loads all queue items at once, a 
`load more` button will appear at the bottom of the page, allowing you to load 
more items to your current queue.

## Subreddit Settings

The Subreddit Settings page is used to set up or modify default actions and 
usernotes for a given subreddit. These settings are stored on Reddit, and are 
shared across all members of a team using Modpanel, across any number of 
instances. There are two sets of settings found on this page.


### Removal Types for Notes
The notes set up with Moderator Toolbox on Reddit will be displayed here, with 
dropdown selectors determining the automatic action which corresponds to each 
note when performing a removal. The options are:

* `None` - Display this note, but do nothing.
* `Do Not Display` - Hide notes of this type in the removals panel.
* `Remove` - Remove the post.
* `Temporary Ban` - Remove the post, temporarily ban the user.
* `Permanent Ban` - Remove the post, permanently ban the user.

If your subreddit uses the default Moderator Toolbox Notes, Modpanel will 
pre-configure those notes to their appropriate actions; if you've customized 
your notes you'll need to map them manually before they'll be available when 
removing a post.

Two additional settings appear in this panel:

* `Action for no usernote` is the action to perform when not issuing a usernote 
with a removal. Defaults to `None`, but if your team *doesn't* log every 
removal with a note, setting this to `Remove` may be useful. You cannot set 
this action to `Do Not Display`.
* `Default Temporary Ban Days` is the number of days that a Temporary Ban 
should be set for if not otherwise specified.

### Default Usernotes
In this panel, you'll find a list of your Toolbox removal reasons, and a text 
field allowing you to enter a default note which will be entered when selecting 
that reason. Notes that are left blank will not be autofilled.

**Please Note:** Modpanel has no way of pinning a note to a specific removal 
reason and this is a simple list; if you reorder or add/remove Toolbox Removal 
Reasons on Reddit, you'll need to reorder your default notes.

## User Page
Available for any user at `user/<username>` (or by clicking the `overview` 
button on a [queue page](pages.md#queue-page), where `<username>` is the name 
of a Redditor. Fetches the 50 most recent posts and comments by that user, with 
the option to load more at the bottom. You can optionally hide posts you're 
unable to mod, posts that have already been modded by a member of your team, or 
both. You cannot *currently* moderate posts from this page.

## Admin Page

This page, viewable only to users marked as admins, is used to administer 
Modpanel. Currently, only user management may be done through this interface.

Through this page, you can make users Modpanel administrators (or remove their 
admin privileges), mark users as active or inactive, delete their saved Reddit 
OAuth2 token, or delete the user.

Token deletion may occasionally be necessary for a user - sometimes Reddit 
won't properly refresh a token, and Modpanel isn't always smart enough to 
detect when a user needs to reauthenticate.

**Please Note:** There are currently *zero* safety precautions here; Modpanel 
will happily let you remove admin privileges from everyone, requiring you to 
need to manually edit the user database to restore admin privileges. 

## Diff Page

The Diff page is not directly exposed anywhere in the UI, it is available at 
`post/diff/<post id>`, where `<post id>` is the id of a post you want to view 
edits on.

The Diff page allows you to enter a post id for a Reddit post, view edits to a 
post compared to the version archived on Pushshift, if available. The intended 
usage for this page is to compare edits to see if a removed post which has been 
edited is suitable to be approved; as such, there is an approve button at the 
bottom of the post.

Three tabs are available:

* `Pushshift` - Allows you to see the post as archived on Pushshift
* `Difference` - The default tab, which shows you an inline difference between 
the current version of the post and the archived version from Pushshift. 
Deletions are struck through and highlighted in Red, additions are highlighted 
in Green.
* `Current` - The current version of the post.

## Search Page

Search backed by either reddit's built in search, or by pushshift.