/*
 * @file Manages all library initialization, jQuery callbacks, query entry
 *      callbacks, server querying, and results diplay for `index.html`.
 */

var advancedSearchDiv = $("div#advanced-search");
var advancedSearchButton = $("button#advanced-search");
FINISH_TYPING_INTERVAL = 650;
var searchBar = $("form#search-bar input[type='text']")[0];
var resultsDiv = $("div#results")[0];

var typingTimer, scrollTimer, lastValue;
var searchResultsPage = 1;

/*
 * Set all page callbacks.
 */
(function setHomePageCallbabacks(){
    var results = $('#results').get(0);

    // Enable infinite scrolling down the results page.
    $(window).scroll(function(){
        if($(window).scrollTop() + $(window).height() == $(document).height() &&
                resultsDiv.querySelectorAll(".result").length > 0)
            loadMoreResults();

        clearTimeout(scrollTimer);
        if (!results.classList.contains('disable-hover'))
            results.classList.add('disable-hover')

        scrollTimer = setTimeout(function(){
            if (results.classList.contains('disable-hover'))
                results.classList.remove('disable-hover');
        }, 200);
    });

    // Toggle the advanced-search form's visibility.
    advancedSearchButton.click(function(){
        var searchField = $("div#search-field");
        if(!advancedSearchDiv.hasClass("visible")){
            searchField.addClass("partly-visible");
            advancedSearchDiv.fadeIn(500).addClass("visible");
            advancedSearchButton.addClass("clicked");
        }
        else {
            advancedSearchDiv.hide().removeClass("visible");
            advancedSearchButton.removeClass("clicked");
            if($("div#results .result").length == 0)
                searchField.removeClass("partly-visible");
            clearResults();
        }
    });

    // Enable capturing the `enter` key.
    $("form#search-bar").submit(function(event){
        event.preventDefault();
        return false;
    });
    searchBar.onkeyup = typingTimer;
}());

/*
 * Set keyboard shortcut mappings.
 */
(function resultsHotkeys(){
    /*
     * If the currently viewed result is not the first, scroll to the previous
     * result.
     */
    var previousResult = function(){
        var currResult = $(".display-all");
        if(currResult.length) {
            currResult.removeClass("display-all");
            currResult = currResult.closest(".result").prev(".result");
        } else {
            currResult = $(document.querySelectorAll(".result")[0]);
        }

        currResult.addClass("display-all");
        currResult.each(function(){
            $('html,body').stop().animate({
                scrollTop: $(this).offset().top - (
                    $(window).height() - $(this).outerHeight(true)) / 2
            }, 140);
        });
    };

    /*
     * If the currently viewed result is not the last, scroll to the next
     * result.
     */
    var nextResult = function(){
        var currResult = $(".display-all");
        if(currResult.length) {
            currResult.removeClass("display-all");
            currResult = currResult.closest(".result").next(".result");
        } else {
            currResult = $(document.querySelectorAll(".result")[0]);
        }

        currResult.addClass('display-all');
        currResult.each(function(){
            $('html,body').stop().animate({
                scrollTop: $(this).offset().top - (
                    $(window).height() - $(this).outerHeight(true)) / 2
            }, 140);
        });
    };

    var displayHotkeyHelp = function(){
        var help = $("div#hotkey-help");
        if(help.hasClass("hidden"))
            help.fadeIn(420);
        else
            help.fadeOut(420);

        $("div#body").toggleClass("faded");
        help.toggleClass("hidden");
    }

    var hotkeyActions = {
        "k" : previousResult,
        "j" : nextResult,
        "h" : previousSymbolMatch,
        "l" : nextSymbolMatch,
        "?" : displayHotkeyHelp
    };

    $(window).keypress(function(key){
        for(var hotkey in hotkeyActions){
            var keyChar = String.fromCharCode(key.keyCode);
            if(keyChar == hotkey &&
                !($(key.target).is("textarea") || $(key.target).is("input")))
                hotkeyActions[keyChar]();
        }
    });
}());

// Enable infinite scrolling down the results page.
$(window).scroll(function() {
    var searchField = $("div#search-field");
    if($(window).scrollTop() + $(window).height() == $(document).height() &&
        searchField.hasClass('partly-visible')){
        loadMoreResults();
    }
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
        searchField.addClass("partly-visible");
        populateResults();
    }
    else {
        searchField.removeClass("partly-visible");
        $("div#advanced-search").fadeOut(50);
        advancedSearchButton.removeClass("clicked");
        clearResults();
    }
}

/*
 * Removes any child elements of `div#results`.
 */
function clearResults(){
    while(resultsDiv.firstChild)
        resultsDiv.removeChild(resultsDiv.firstChild);
}

/*
 * Create a result element based upon a codelet instance.
 *
 * @return {Element} The result element.
 */
function createResult(codelet) {
    var maxAttributeLength = 20;

    //Level 1
    var newDiv = document.createElement("div"),
        table = document.createElement("table"),
        row = document.createElement("tr");
    //Level 2
    var displayInfo = document.createElement("div"),
        codeElt = document.createElement("td"),
        hiddenInfoContainer = document.createElement("td"),
        hiddenInfo = document.createElement("div"),
        cycle = document.createElement("div");
    //Level 3
    var title = document.createElement("span"),
        site = document.createElement("span"),
        nextMatch = document.createElement("a"),
        prevMatch = document.createElement("a"),
        dateModified = document.createElement("div"),
        language = document.createElement("div"),
        dateCreated = document.createElement("div"),
        authors = document.createElement("div");

    //Classes and ID's
    newDiv.classList.add('result');

    displayInfo.id = 'display-info';
    codeElt.id = 'code';
    hiddenInfo.id = 'hidden-info';
    cycle.id = 'cycle-matches'

    title.id = 'title';
    site.id = 'site';
    nextMatch.id = 'next-match';
    nextMatch.href = '#';
    prevMatch.id = 'prev-match';
    prevMatch.href = '#';
    dateModified.id = 'date-modified';
    language.id = 'language';
    dateCreated.id = 'date-created';
    authors.id = 'authors';

    //Add the bulk of the html
    title.innerHTML = ' &raquo; <a href="' + codelet.url + '">'
            + codelet.name + '</a>';
    site.innerHTML = '<a href="' + codelet.origin[1] + '">' +
            codelet.origin[0] +'</a>';
    nextMatch.innerHTML = 'next match';
    prevMatch.innerHTML = 'prev match';
    language.innerHTML = 'Language: <span>' + codelet.lang + '</span>';
    dateModified.innerHTML = 'Last modified: <span>' + codelet.modified +
            '</span>';
    // Needs to be changed from int to string on the server
    dateCreated.innerHTML = 'Created: <span>' +
            codelet.created.substring(0, maxAttributeLength) + '</span>';

    var authorsHtml = 'Authors: <span>';
    var currLength = 0;
    var authorsList = [];
    for(var auth = 0; auth < codelet.authors.length; auth++){
        currLength += codelet.authors[auth].length;
        if(maxAttributeLength < currLength){
            authorsList.push("...");
            break;
        }
        else
            authorsList.push('<a href=#>' + codelet.authors[auth] + '</a>');
    }
    authors.innerHTML = "Authors: <span>" + authorsList.join(", ") + "</span>";

    // Needs to be processed on the server
    codeElt.innerHTML = '<div id=tablecontainer>' + codelet.code + '</div>';

    //Event binding
    $(newDiv).on('mousemove', function(e) {
        var holdCondition = $('.disable-hover');

        if(holdCondition.length == 0) {
            $(this).siblings().removeClass('display-all');
            $(this).addClass('display-all');
        }
    });

    $(newDiv).on('mouseleave', function(e) {
        var holdCondition = $('.disable-hover');

        if(holdCondition.length == 0)
            $(this).removeClass('display-all');
    });

    $(nextMatch).click(function(e) {
        e.stopPropagation();
        e.preventDefault();
        nextSymbolMatch();
    });

    $(prevMatch).click(function(e) {
        e.stopPropagation();
        e.preventDefault();
        previousSymbolMatch();
    });

    //Finish and append elements to parent elements
    hiddenInfo.appendChild(dateCreated);
    hiddenInfo.appendChild(dateModified);
    hiddenInfo.appendChild(language);
    hiddenInfo.appendChild(authors);

    hiddenInfoContainer.appendChild(hiddenInfo);

    row.appendChild(codeElt);
    row.appendChild(hiddenInfoContainer);
    table.appendChild(row);

    displayInfo.appendChild(site);
    displayInfo.appendChild(title);

    cycle.appendChild(prevMatch);
    cycle.appendChild(nextMatch);

    newDiv.appendChild(displayInfo);
    newDiv.appendChild(table);

    return newDiv;
}

function previousSymbolMatch() {
    var currResult = $(".display-all"),
        currMatch = currResult.find(".hll.current"),
        matches = currResult.find(".hll"),
        scrollDiv = currResult.find("#tablecontainer");

    if (currMatch.length == 0)
        currMatch = matches[0];
    else
        currMatch.removeClass('current');

    var index = matches.index(currMatch.get(0)) - 1;
    index = index <= 0 ? matches.length - 1 : index;
    var newMatch = $(matches[index]);

    scrollDiv.scrollTop(scrollDiv.scrollTop()
            - scrollDiv.height() / 2
            + newMatch.position().top + newMatch.height() / 2);

    newMatch.effect("highlight", {color: '#FFF'}, 750)
    newMatch.addClass('current');
};

function nextSymbolMatch() {
    var currResult = $(".display-all"),
        currMatch = currResult.find(".hll.current"),
        matches = currResult.find(".hll"),
        scrollDiv = currResult.find("#tablecontainer");

    if (currMatch.length == 0)
        currMatch = $(matches[0]);
    else
        currMatch.removeClass("current");

    var index = matches.index(currMatch.get(0)) + 1;
    index = index >= matches.length ? 0 : index;
    var newMatch = $(matches[index]);

    scrollDiv.scrollTop(scrollDiv.scrollTop()
            - scrollDiv.height() / 2
            + newMatch.position().top + newMatch.height() / 2);

    newMatch.effect("highlight", {color: "#FFF"}, 750)
    newMatch.addClass("current");
};

/*
 * AJAX the current query string to the server, and return its response.
 *
 * @return {Array} The server's response in the form of `div.result` DOM
 *      elements, to fill `div#results`.
 */
function queryServer(){
    var queryUrl = document.URL + "search.json?" + $.param({
        "q" : searchBar.value,
        "p" : searchResultsPage++,
        "hl": 1
    });

    var results = $.Deferred();
    $.getJSON(queryUrl, function(result){
        var resultDivs = [];
        if("error" in result)
            insertErrorMessage(result["error"]);
        else if(result["results"].length == 0 && searchResultsPage == 2)
            insertErrorMessage("No search results.");
        else
            for(var codelet = 0; codelet < result["results"].length; codelet++)
                resultDivs.push(createResult(result["results"][codelet]));
        results.resolve(resultDivs);
    });

    return results;
}

/*
 * Query the server with the current search string, and populate `div#results`
 * with its response.
 */
function populateResults(){
    searchResultsPage = 1;
    loadMoreResults();
}

/*
 * Query the server for the next results page, and add its codelets to
 * `div#results`.
 */
function loadMoreResults(){
    queryServer().done(function(results){
        for(var result = 0; result < results.length; result++){
            var newDiv = results[result];
            resultsDiv.appendChild(newDiv);
            setTimeout(
                (function(divReference){
                    return function(){
                        divReference.classList.add("cascade");
                    };
                }(newDiv)),
                result * 20);
        }
    });
}

/*
 * Displays a warning message in the UI.
 *
 * @param msg (str) The message string.
 */
function insertErrorMessage(msg){
    var error = $(
            [
                "<div id='error'><span id='s1'>Error</span> ",
                "<span id='s2'>&raquo;</span> </div>"
            ].join(""));
    error.append(msg);
    resultsDiv.appendChild(error[0]);
}
