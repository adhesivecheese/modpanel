(function() {
	try {
		var burger = document.querySelector('.burger');
		var menu = document.querySelector(`#${burger.dataset.target}`);
		burger.addEventListener('click', function() {
				burger.classList.toggle('is-active');
				menu.classList.toggle('is-active');
		});
	} catch {
		//do nothing if no burger
	}
})();

function openTab(evt, tabName, id) {
	document.querySelectorAll(`.content-tab-${id}`).forEach( content_tab => { content_tab.style.display = "none" })
	document.querySelectorAll(`.tab-${id}`).forEach( tab => { tab.classList.remove("is-active") })
	document.getElementById(tabName).style.display = "block"
	evt.currentTarget.classList.add("is-active")
}



function collapse_body(ele){
	element = document.getElementById(`collapsible-${ele}`)
	arrow = document.getElementById(`arrow-${ele}`)
    if (element.classList.contains("is-active")){
		element.classList.remove("is-active")
		arrow.innerHTML = "▼"
	} else {
		element.classList.add("is-active")
		arrow.innerHTML = "▲"
	}
}