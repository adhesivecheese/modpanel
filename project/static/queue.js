sub = window.location.pathname.split("/")[1]
queue = window.location.pathname.split("/")[3]
var reasons

function script_loaded() {
	bulmaQuickview.attach()
	set_timestamps() 
	add_image_expandos()
	modlog_events = new EventSource(`/log?sub=${sub}`)
	from_modlog(modlog_events)
	window.addEventListener('beforeunload', () => { modlog_events.close(); });

	reasons = JSON.parse(document.querySelector("#defaultNotes").innerHTML).defaultNotes
}

function action_button_clicked(postID, action) {
	var approveButton = document.getElementById(`btn-approve-${postID}`)
	var removeButton = document.getElementById(`btn-remove-${postID}`)

	if (action == "Approved") {
		approveButton.classList.remove("is-loading")
		approveButton.disabled = false
		approveButton.innerHTML = action
		approveButton.classList.remove("is-light")
		removeButton.innerHTML = "Remove"
		removeButton.classList.add("is-light")
	} else {
		removeButton.classList.remove("is-loading")
		removeButton.disabled = false
		removeButton.innerHTML = action
		removeButton.classList.remove("is-light")
		approveButton.innerHTML = "Approve"
		approveButton.classList.add("is-light")
	}
}

function approve_post(postID) {
	updateQueueCount()
	closeRemovals(true)
	approveButton = document.getElementById(`btn-approve-${postID}`)
	approveButton.innerHTML = "Approving"
	approveButton.classList.add("is-loading")
	approveButton.disabled = true
	onDone = function () { if (this.readyState == 4 && this.status == 200) { action_button_clicked(postID, "Approved") } }
	make_ajax_request(onDone,`postID=${postID}&action=approve`)
}

function primeRemoval(event, postID, author) {
	if (event.shiftKey) { quickRemove(postID, "silent") }
	else if (author == "[deleted]") { quickRemove(postID, "silent") }
	else if (event.altKey) { quickRemove(postID, "spam")}
	else {
		postTitle = document.querySelector(`#queueitem-${postID} > header > p > a`).innerHTML

		document.querySelector("#removalQuickView").classList.add("is-active")
		document.querySelector("#removalQuickView .quickview-header span").innerHTML = `<a href='#queueitem-${postID}'>${postTitle}</a>`
		document.querySelector("#removalPostID").value = postID

		document.querySelectorAll(`.content-tab-${postID}`).forEach( content_tab => { content_tab.style.display = "none" })
		document.querySelectorAll(`.tab-${postID}`).forEach( tab => { tab.classList.remove("is-active") })
		document.getElementById(`usernotes-${postID}`).style.display = "block"
		document.querySelectorAll(`.tab-${postID}`)[1].classList.add("is-active")

	}
}

function remove_Post(ban, mod) {
	var form = document.forms.namedItem("removalForm")
	var oData = new FormData(form)
	oData.append("action", "remove")
	oData.append("ban", ban)
	insert_note_to_DOM(oData.get("postID"), oData.get("warnType"), oData.get("noteText"), mod)
	closeRemovals(true)
	button = document.getElementById(`btn-remove-${oData.get("postID")}`)
	button.innerHTML = "Removing"
	button.classList.add("is-loading")
	button.disabled = true

	updateQueueCount()
	onDone = function () { if (this.readyState == 4 && this.status == 200) { action_button_clicked(oData.get("postID"), "Removed") }	}
	make_ajax_request(onDone,format_sendData(oData))
}

function quickRemove(postID, type) {
	updateQueueCount()
	button = document.getElementById(`btn-remove-${postID}`)
	button.innerHTML = "Removing"
	button.classList.add("is-loading")
	button.disabled = true
	onDone = function () { if (this.readyState == 4 && this.status == 200) {
			if (type == "spam") { action = "Spammed" } else { action = "Silently Removed" }
			action_button_clicked(postID, action) } }
	make_ajax_request(onDone,`action=quickRemove&type=${type}&postID=${postID}`)
}

function add_note(postID, mod) {
	var form = document.forms.namedItem("addnote-" + postID)
	var oData = new FormData(form)
	oData.append("postID", postID)
	oData.append("action", "addNote")
	onDone = function () { if (this.readyState == 4 && this.status == 200) { insert_note_to_DOM(postID, oData.get("warnType"), oData.get("noteText"), mod) } }
	make_ajax_request(onDone,format_sendData(oData))
}

function ban_user(postID, mod) {
	updateQueueCount()
	var form = document.forms.namedItem("banuser-" + postID)
	var oData = new FormData(form)
	oData.append("postID", postID)
	oData.append("action", "banuser")
	document.getElementById(`banButton-${postID}`).innerHTML = "Banning"
	onDone = function () {
		if (this.readyState == 4 && this.status == 200) {
			insert_note_to_DOM(postID, oData.get("warnType"), oData.get("noteText"), mod)
			document.getElementById(`banButton-${postID}`).innerHTML = "Banned"
		}
	}
	make_ajax_request(onDone,format_sendData(oData))
}

function insert_note_to_DOM(postID, warnType, note, mod) {
	time = luxon.DateTime.now().toFormat('yyyy-LL-dd HH:mm:ss');
	link = `https://redd.it/${postID}` //TODO: Handle Comment links

	newNote = `
	<div class="columns is-gapless" style="margin:0.5rem"> 
		<div class='column is-one-fifth'>
			<a href="https://reddit.com/user/${mod}">/u/${mod}</a>
			<p class='is-size-7'>${time}</p>
		</div>
		<a href='${link}' class='column'>[${warnType}] ${note}</a>
	</div>
	<hr style="margin:0">
	`
	notes = document.getElementById(`extantNotes-${postID}`)
	notes.innerHTML = newNote + notes.innerHTML

	noteCount = parseInt(document.querySelector(`#notecount-${postID}`).innerHTML)
	document.querySelector(`#notecount-${postID}`).innerHTML = noteCount + 1
	document.querySelector(`#notecount-${postID}`).style.display = "block"


}

function updateQueueCount() {
	if (queue == "modqueue") {updateAll = false} else { updateAll = true }
	allCards = document.getElementsByClassName("card").length
	approved = document.getElementsByClassName("card post-approved").length
	removed = document.getElementsByClassName("card post-removed").length
	if (updateAll) {
		approved += document.getElementsByClassName("card post-preapproved").length
		removed += document.getElementsByClassName("card post-preremoved").length
	}
	document.getElementById("queuecount").innerHTML = allCards - approved - removed
}

function closeRemovals(clear=false) {
	document.querySelector("#removalQuickView").classList.remove("is-active")
	if (clear) {
		document.forms.namedItem("removalForm").reset()
		document.querySelectorAll(".removal-text").forEach(reason => { reason.classList.add("is-hidden") })
		document.querySelector("#userBanMessage").style.display = "none"
		document.getElementById("removalActionTarget").innerHTML = ""
		var target = document.getElementById("removalActionTarget")
		target.innerHTML = ''
		document.querySelector("#userBanMessage").style.display = "none"
		document.getElementsByClassName("quickview-body")[0].scrollTop = 0
	}
}


function from_modlog(source) {
	source.onmessage = function (event) {
		activeMins = 15
		var data = event.data;
		//console.debug("got message from Server: " + data)
		data = data.split(" |-| ");
		timestamp = data[0]
		moderator = data[1]
		fullname = data[2]
		modaction = data[3]

		if (queue == "modqueue") {updateAll = false} else { updateAll = true }

		try {
			id = fullname.split("_")[1]
			card = document.getElementById("queueitem-" + id)

			if (modaction == "approvelink" || modaction == "approvecomment") {
				card.classList.remove(...card.classList)
				card.classList.add('card','post-approved')
				document.getElementById("btn-approve-" + id).innerHTML = "Approved (by " + moderator + ")"
				updateQueueCount()
				if (document.getElementById("userreportlink-" + id)) {
					document.getElementById("userreportlink-" + id).remove()
				}
				if (document.getElementById("modreportlink-" + id)) {
					document.getElementById("modreportlink-" + id).remove()
				}
			} else if (modaction == "removelink" || modaction == "removecomment") {
				card.classList.remove(...card.classList)
				card.classList.add('card','post-removed')
				document.getElementById("btn-remove-" + id).innerHTML = "Removed (by " + moderator + ")"
				updateQueueCount()
				if (document.getElementById("userreportlink-" + id)) {
					document.getElementById("userreportlink-" + id).remove()
				}
				if (document.getElementById("modreportlink-" + id)) {
					document.getElementById("modreportlink-" + id).remove()
				}
			} else if (modaction == "spamlink" || modaction == "spamcomment") {
				card.classList.remove(...card.classList)
				card.classList.add('card','post-removed')
				document.getElementById("btn-remove-" + id).innerHTML = "Spammed (by " + moderator + ")"
				updateQueueCount()
				if (document.getElementById("userreportlink-" + id)) {
					document.getElementById("userreportlink-" + id).remove()
				}
				if (document.getElementById("modreportlink-" + id)) {
					document.getElementById("modreportlink-" + id).remove()
				}
			}
		} catch {
			//console.debug("saw " + modaction + " on item not currently in loaded queue")
		}

		var activeDiv = `
			<li class='modactive' id='_${moderator}-active' data-timestamp='${data[0]}'>
				<div class='columns is-size-7 _${moderator}'>
					<div class='column'>${moderator}</div>
					<div class='column is-size-7 mt-1 _${moderator} timestamp' data-timestamp='${data[0]}'>${timestamp}</div>
				</div>
			</li>
		`
		targetDiv = document.querySelector(`#_${moderator}-active`)
		if (targetDiv) {
			targetDiv.setAttribute("data-timestamp", data[0]);
			document.querySelector(`._${moderator} .timestamp`).setAttribute("data-timestamp", data[0]);
		} else {
			document.querySelector('#activeInfo').innerHTML += activeDiv
		}
		update_active_mods(activeMins)
	};
}

function toggleReason(identifier) {
	check = document.getElementById("check-" + identifier)
	element = document.getElementById("reason-" + identifier)
	if (check.checked == true) {
		element.classList.remove("is-hidden")
	} else {
		element.classList.add("is-hidden")
	}

	textString = ""
	for (var i = 0; i < document.getElementsByClassName("removalCheckbox").length; i++){
		check = document.getElementById("check-" + i)
		if (check.checked==true) {
			if(textString != "") {textString += ", "}
		textString += reasons[i+1].note
		}
	}
	textString = textString.replace(', ,', ',')

	document.getElementById('noteText').value = textString

}

function delete_usernote(user, timestamp, postID) {
	deleteButton = document.querySelector(`#delnote-${postID}-${timestamp}`)
	deleteButton.classList.add("is-loading")
	deleteButton.disabled = true
	onDone = function () {
		if (this.readyState == 4 && this.status == 200) {
			document.querySelectorAll(`[data-usernote="un-${user}-${timestamp}"]`).forEach(deleted_note => {
				deleted_note.remove()
				noteCount = parseInt(document.querySelector(`#notecount-${postID}`).innerHTML)
				if (noteCount == 1) { document.querySelector(`#notecount-${postID}`).style.display = "none" }
				else { document.querySelector(`#notecount-${postID}`).innerHTML = noteCount - 1	}
			})
		}
	}
	make_ajax_request(onDone, `postID=${postID}&action=deleteNote&user=${user}&timestamp=${timestamp}`)
}