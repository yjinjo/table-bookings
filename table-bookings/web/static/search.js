let currentPage = 1;
let isEndOfScroll = false;

window.onload = function() {
  window.addEventListener('scroll', function(event)
  {
      let element = window.document.scrollingElement;
      if (element.scrollHeight - element.scrollTop === element.clientHeight && !isEndOfScroll)
      {
          fetchData();
      }
  });
};

function fetchData() {
    let keyword = document.getElementById('result-keyword').value;
    let category = document.getElementById('result-category').value;
    let start = document.getElementById('result-start').value;
    let end = document.getElementById('result-end').value;
    let weekday = document.getElementById('result-weekday').value;

    currentPage ++;

    let httpRequest = new XMLHttpRequest();
    httpRequest.addEventListener("load", (e) => {
        let jsonResponse = JSON.parse(e.target.responseText);
        console.log(jsonResponse)
        jsonResponse.forEach(data => appendItem(data));
        if (jsonResponse.length < 8) isEndOfScroll = true;
    });
    httpRequest.open("GET", "/search/json/?page=" + currentPage
        + "&keyword=" + keyword + "&category=" + category + "&start=" + start + "&end=" + end + "&weekday=" + weekday);
    httpRequest.send();
}

function appendItem(data) {
    let template = document.getElementById("restaurant-template");
    let body = document.getElementById("search-result")
    let clone = template.content.cloneNode(true);
    clone.querySelector(".item-category").textContent = data.category_name;
    clone.querySelector(".item-name").textContent = data.name;
    clone.querySelector(".item-address").textContent = data.address;

    if (clone.querySelector(".item-link") != null) {
    	let link = clone.querySelector(".item-link").href;
	    link = link.replace("/0/", "/" + data.id + "/");
	    clone.querySelector(".item-link").href = link;
    }

    let finalUrl = data.image.replace("/media/https%3A", "https:/"); // 외부 url 대응
    clone.querySelector(".item-image").src = finalUrl;

    body.appendChild(clone);
}
