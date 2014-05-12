/*
 * @file Manages all query entry, `index.html` server querying, and results
 *      diplay.
 */

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
    if(lastValue != searchBar.value)
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
    lastValue = searchBar.value;
    var searchField = document.querySelectorAll("div#search-field")[0]

    clearResults();
    if(searchBar.value){
        populateResults();
        if(!searchField.classList.contains("partly-visible"))
            searchField.classList.add("partly-visible");
    }
    else
        searchField.classList.remove("partly-visible");
}

/*
 * Removes any child elements of `div#results`.
 */
function clearResults(){
    var resultsPage = document.querySelectorAll("div#results")[0];

    while(resultsPage.firstChild)
        resultsPage.removeChild(resultsPage.firstChild);
}

/*
 * Query the server with the current search string, and populate `div#results`
 * with its response.
 */
function populateResults(){
    var resultsPage = document.querySelectorAll("div#results")[0];
    var results = queryServer();

    for(var result = 0; result < results.length; result++){
        var newDiv = results[result];
        resultsPage.appendChild(newDiv);
        setTimeout(
        (function(divReference){
            return function(){
                divReference.classList.add("cascade");
            };
        }(newDiv)), result * 20);
    }

    for(var result = 0; result < results.length; result++);
}

/*
 * AJAX the current query string to the server, and return its response.
 *
 * @return {Array} The server's response in the form of `div.result` DOM
 *      elements, to fill `div#results`.
 */
function queryServer(){
    var resultDivs = []
    for(var result = 0; result < 200; result++){
        var newDiv = document.createElement("div");
        newDiv.classList.add("result");
        newDiv.innerHTML = Math.random();
        newDiv.style.textAlign = "center";
        newDiv.style.color = "#" + Math.floor(Math.random() *
                16777215).toString(16);
        resultDivs.push(newDiv)
    }

    return resultDivs;
}
