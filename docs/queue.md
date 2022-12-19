# Moderating on Modpanel

## Colors and What They Mean

The individual card backgrounds in Modpanel will turn colors when they're 
actioned by you (or your fellow moderators), and that action has registered 
with Reddit's modlog and been reported back to Modpanel. A Green background 
indicates that a post has been approved, whereas a red background indicates that
a post has been removed. Background colors provide additional feedback; this may 
lag for a number of seconds before registering.

Items which have been filtered by AutoModerator will appear with a light red 
titlebar.


## Approving Posts

Simply hit the `Approve` button on a queue item to approve the post. The button 
will disable while processing to prevent dupicate requests to the server, and 
the Approve text will disapear in favor of a spining icon. When the request has 
processed on the Modpanel server, the button will turn a different shade of 
green, and the text will read `Approved`. The background of the card will turn 
green when the action has been registered on Reddit as an additional check.

## Removing Posts

Removing a post starts, logically enough, with clicking the `Remove` button. 
Simply clicking this button **does not** remove the post on it's own; it simply 
opens the removal panel, which slides out from the left. The item's title will 
appear at the top of the removal panel to ensure you've selected the item you 
intend. This title is an anchor link to the item in your currently-loaded queue, 
allowing you to jump back to it should you accidentally scroll away.

Below the title you'll find the removal reasons from Moderator Toolbox; be aware 
that you can click anywhere on the line with the removal reason to trigger the 
checkbox, not just the small box itself. If you or a teammate have filled in 
default notes in Modpanel's [Subreddit Settings](pages.md#subreddit-settings), 
the appropriate notes will appear as a comma-seperated list in the usernote box 
at the bottom of the removal panel. **Please Note:** selecting or deselecting a 
removal reason will overwrite anything manually entered into the `Usernote` 
field - if you wish to input a custom note, do so *after* you have selected all 
your reasons.

Selecting a note type will bring up the appropriate Remove or Ban button at the 
bottom left of the removal panel. (Missing note types? Ensure you've mapped them 
in [Subreddit Settings](pages.md#subreddit-settings) for your subreddit!)

If you're issuing a ban, an additional text box, "Ban Message to User", will
appear below the usernote row, allowing you to leave a message for the user.

Clicking the button which has appeared (which will either read `Remove`, 
`Temporary Ban` and a ban duration selector, or `Permanent Ban`) will remove 
the post, leave the usernote, and (if applicable) ban the user temporarily or 
permanently as one action.

### Special removals

* If removing a post from a deleted user, Modpanel will bypass the removal panel 
and simply silently remove the post or comment.
* Holding the Shift key while clicking the Remove button will similarly bypass 
the removal panel, and will silently remove the post.
* Holding Alt while pressing the Remove button will mark the post as spam when 
it's removed.

## Bans
One of the tabs offered at the top of a queue item is "Ban". This tab is mostly 
useful for spammers and other serious offenses you don't want to offer feedback 
on with a full removal. The User Note field leaves a permanent ban toolbox 
usernote, as well as setting the ban note on Reddit. Selecting the `Spam Post` 
checkbox before clicking the ban button will spam the post. Selecting the `Wipe 
History` checkbox before clicking the Ban User button will go through a user's 
visible post history and remove any post or comment the user has ever made to 
the subreddit you're on the queue for. Wipe history can take a minute, and does 
not currently offer feedback on it's progress.