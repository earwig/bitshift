/*
 * @file Manages all library initialization, jQuery callbacks, query entry
 *      callbacks, server querying, and results diplay for `index.html`.
 */

var advancedSearchDiv = $("div#advanced-search");
var advancedSearchButton = $("button#advanced-search");
advancedSearchDiv.hide();
advancedSearchButton.click(function(){
    if(!advancedSearchDiv.hasClass("visible")){
        advancedSearchDiv.fadeIn(500);
        advancedSearchDiv.addClass("visible");
    }
    else {
        advancedSearchDiv.fadeOut(300);
        advancedSearchDiv.removeClass("visible");
    }
});

$(function() {
    $("#date-last-modified").datepicker();
    $("#date-created").datepicker();
});

var languages = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace("value"),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    local: $.map(TYPEAHEAD_LANGUAGES, function(state){
        return {value : state};
    })
});

languages.initialize();
$("#languages.typeahead").typeahead({
        hint: true,
        highlight: true,
        minLength: 1
    },
    {
        name: "languages",
        displayKey: 'value',
        source: languages.ttAdapter()
});

FINISH_TYPING_INTERVAL = 650;
searchBar = $("form#search-bar input[type='text']")[0];
resultsDiv = $("div#results")[0];

var typingTimer, lastValue;
searchBar.onkeyup = typingTimer;

// Enable infinite scrolling down the results page.
$(window).scroll(function() {
    if($(window).scrollTop() + $(window).height() == $(document).height()){
        loadMoreResults();
    }
});

// Enable capturing the `enter` key.
$("form#search-bar").submit(function(event){
    event.preventDefault();
    return false;
});

/*
 * Clear the existing timer and set a new one the the user types text into the
 * search bar.
 */
function typingTimer(event){
    clearTimeout(typingTimer);

    var enterKeyCode = 13;
    if(event.keyCode != enterKeyCode){
        if(lastValue != searchBar.value)
            typingTimer = setTimeout(finishedTyping, FINISH_TYPING_INTERVAL);
    }
    else {
        event.preventDefault();
        finishedTyping();
        return false;
    }
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
    var searchField = $("div#search-field");

    clearResults();
    if(searchBar.value){
        if(!searchField.hasClass("partly-visible"))
            searchField.addClass("partly-visible");

        populateResults();
    }
    else
        searchField.removeClass("partly-visible");
}

/*
 * Removes any child elements of `div#results`.
 */
function clearResults(){
    while(resultsDiv.firstChild)
        resultsDiv.removeChild(resultsDiv.firstChild);
}

/*
 * Query the server with the current search string, and populate `div#results`
 * with its response.
 */
function populateResults(){
    var results = queryServer();

    for(var result = 0; result < results.length; result++){
        var newDiv = results[result];
        resultsDiv.appendChild(newDiv);
        setTimeout(
            (function(divReference){
                return function(){
                    divReference.classList.add("cascade");
                };
            }(newDiv)), result * 20);
    }
}

/*
 * AJAX the current query string to the server, and return its response.
 *
 * @return {Array} The server's response in the form of `div.result` DOM
 *      elements, to fill `div#results`.
 */
function queryServer(){
    var resultDivs = []
    for(var result = 0; result < 20; result++){
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

/*
 * Adds more results to `div#results`.
 */
function loadMoreResults(){
    results = queryServer();
    for(var result = 0; result < results.length; result++){
        var newDiv = results[result];
        resultsDiv.appendChild(newDiv);
        setTimeout(
            (function(divReference){
                return function(){
                    divReference.classList.add("cascade");
                };
            }(newDiv)), result * 20);
    }
}
