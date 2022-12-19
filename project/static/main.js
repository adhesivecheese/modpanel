setInterval(set_timestamps, 60000)
function set_timestamps() {
	document.querySelectorAll(".timestamp").forEach(timediv => {
		timestamp = parseInt(timediv.dataset.timestamp)
		const diffSeconds = parseInt(Math.floor(Date.now() / 1000) - timestamp)
		if (diffSeconds < 60) { timediv.innerHTML = "Just Now" }
		else { timediv.innerHTML = luxon.DateTime.fromSeconds(timestamp).toRelative() }
		timediv.title = luxon.DateTime.fromSeconds(timestamp).toJSDate()
	})
	document.querySelectorAll(".timestamp-absolute").forEach(timediv => {
		timestamp = parseInt(timediv.dataset.timestamp)
		timediv.innerHTML = luxon.DateTime.fromSeconds(timestamp).toFormat('yyyy-LL-dd HH:mm:ss');
		timediv.title = luxon.DateTime.fromSeconds(timestamp).toRelative()
	})
}
function update_active_mods(cuttoffMins=15) {
	var moddivs = document.querySelectorAll(".modactive")
	set_timestamps() 
	moddivs.forEach(mod => {
		timestamp = parseInt(mod.dataset.timestamp)
		cuttoffTime = parseInt(Math.floor(Date.now() / 1000)) - (cuttoffMins * 60)
		if (timestamp < cuttoffTime) { mod.remove() }
	})
}


function format_sendData(oData) {
	var sendData = ""
	for (var key of oData.keys()) {	sendData += `${key}=${encodeURIComponent(oData.get(key))}&`	}
	return sendData
}
function make_ajax_request(onDone, sendData, path=window.location.pathname) {
	var req = new XMLHttpRequest()
	req.onreadystatechange = onDone
	path = path.split("#")[0]
	req.open("POST", path, true)
	req.setRequestHeader("content-type", "application/x-www-form-urlencoded;charset=UTF-8")
	req.send(sendData)
}


function add_image_expandos() {
	var list = document.querySelectorAll(".content a")
	for (let item of list) {
		link = item.href
		if (
			link.includes("imgur") ||
			link.endsWith(".png") ||
			link.endsWith(".jpg")
		) {
				if (!item.nextElementSibling) {
				var node = document.createElement("button")
				node.setAttribute("onclick", `imgExpand("${link}")`)
				var textnode = document.createTextNode("+")
				node.appendChild(textnode)
				item.after(node)
			}
		}
	}
}
function imgExpand(link) {
	els = document.querySelector(`a[href="${link}"]`).nextElementSibling
	els.innerHTML = "-"
	if (!link.includes(".jpg")) { link = link.split("?")[0] + ".jpg" }
	var img = document.createElement("img")
	img.src = link
	img.style.width = document.querySelector(".card").clientWidth - 50 + "px"
	img.classList.add("resizeable")
	img.addEventListener("mousedown", mousedown)

	function mousedown(e) {
		e.preventDefault()
		currentresizeable = e.target
		let prevX = e.clientX
		window.addEventListener("mousemove", mousemove)
		window.addEventListener("mouseup", mouseup)
		function mousemove(e) {
			const rect = currentresizeable.getBoundingClientRect()
			currentresizeable.style.width = rect.width - (prevX - e.clientX) + "px"
			prevX = e.clientX
		}
		function mouseup() {
			window.removeEventListener("mousemove", mousemove)
			window.removeEventListener("mouseup", mouseup)
		}
	}
	if (!els.nextElementSibling || els.nextElementSibling.id != link) {
		node = document.createElement("div")
		node.id = link
		els.after(node)
	}
	iels = els.nextElementSibling
	if (!iels.hasChildNodes()) { iels.appendChild(img) }
	else {
		if (iels.style.display == "none") {
			els.innerHTML = "-"
			iels.style.display = "block"
		} else {
			els.innerHTML = "+"
			iels.style.display = "none"
		}
	}
}


function load_more(after) {
	button = document.getElementById("loadMore")
	button.classList.add("is-loading")
	button.disabled = true
	button.id = "loadingMore"
	button.innerHTML="Moreing..."

	onDone = function () {
		if (this.readyState == 4 && this.status == 200) {
			document.getElementById("items").innerHTML += this.response
			document.getElementById("loadingMore").remove()
			set_timestamps()
			updateQueueCount()
			add_image_expandos()
			try {
				if (document.getElementById("hideUnmod").checked) {hide_unmoderateable()}
				if (document.getElementById("hideModded").checked) {hide_modded()}
			} catch {}
		}
	}

	make_ajax_request(onDone, `thingID=${after}`, `${window.location.pathname}/more`)

}
