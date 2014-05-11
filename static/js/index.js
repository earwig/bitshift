FINISH_TYPING_INTERVAL = 650;
searchBar = document.querySelectorAll("form#search-bar input[type='text']")[0];

var typingTimer, lastValue;
searchBar.onkeyup = typingTimer;

/*
 * Clear the existing timer and set a new one the the user types text into the
 * search bar.
 */
function typingTimer(){
    clearTimeout(typingTimer);
    if(lastValue != searchBar.value && searchBar.value)
        typingTimer = setTimeout(finishedTyping, FINISH_TYPING_INTERVAL);
};

/*
 * Callback which queries the server whenver the user stops typing.
 *
 * Whenever the user doesn't type for a `FINISH_TYPING_INTERVAL` after having
 * entered new text in the search bar, send the current query request to the
 * server.
 */
function finishedTyping(){
    queryServer();
    var searchField = document.querySelectorAll("div#search-field")[0]
    if(!searchField.classList.contains("partly-visible"))
        searchField.classList.add("partly-visible");
}

/*
 * AJAX the current query string to the server.
 *
 * Currently just fills `div#results` with random content.
 */
function queryServer(){
    lastValue = searchBar.value;
    var resultsPage = document.querySelectorAll("div#results")[0]

    while(resultsPage.firstChild){
        resultsPage.removeChild(resultsPage.firstChild);
    }

    for(var result = 0; result < 200; result++){
        var newDiv = document.createElement("div");
        newDiv.innerHTML = Math.random();
        newDiv.style.textAlign = "center";
        newDiv.style.color = "#" + Math.floor(Math.random() *
                16777215).toString(16);
        resultsPage.appendChild(newDiv)
    }
}
