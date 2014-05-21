/*
 * @file Manages all advanced search form logic.
 */

var searchGroups = $("div#search-groups");

/*
 * Load all advanced search form libraries.
 */
(function loadInputFieldWidgets(){
    $(".search-group input#date-last-modified").datepicker();
    $(".search-group input#date-created").datepicker();
    $("#autocomplete").autocomplete({
        source: function(request, response){
            var matcher = new RegExp(
                $.ui.autocomplete.escapeRegex(request.term), "i");
            response($.grep(AUTOCOMPLETE_LANGUAGES, function(item){
                return matcher.test(item);
            }));
        }
    });
}());

/*
 * Set all advanced search form button callbacks.
 */
(function setSearchFormCallbacks(){
    // Create a new search group, and update the `#sidebar` checklist.
    $("button#add-group").click(function(){
        $("div#sidebar input[type=checkbox]").prop("checked", false);

        searchGroups.children("#selected").removeAttr("id");
        var searchGroup = $("<div/>", {class : "search-group", id : "selected"});
        searchGroups.append(
                searchGroup.append(createSearchGroupInput("language")));
        $("div#sidebar input[type=checkbox]#language").prop("checked", true);
    });

    // Remove the currently selected group if it's not the only one, and mark
    // one of its siblings as selected.
    $("button#remove-group").click(function(){
        var currentGroup = $("div.search-group#selected");

        if($("div.search-group").length == 1)
            return;
        else {
            var nextGroup = currentGroup.prev();
            if(nextGroup.size() == 0)
                nextGroup = currentGroup.next();
        }
        currentGroup.remove();
        nextGroup.click();
    });

    // Select a search group, and update the `#sidebar` checklist accordingly.
    $(document).on("click", "div.search-group", function(){
        searchGroups.children("#selected").removeAttr("id");
        $(this).attr("id", "selected");
        $("div#sidebar input[type=checkbox]").prop("checked", false);
        $(this).find("input[type=text]").each(function(){
            var checkBoxSelector = "div#sidebar input[type=checkbox]";
            $(checkBoxSelector + "#" + $(this).attr("class").split(" ")[0]).
                    prop("checked", true);
        })
    });

    // Add an input field to the currently selected search group.
    $("div#sidebar input[type=checkbox]").click(function(){
        var fieldId = $(this).prop("id");
        if($(this).is(":checked")){
            $("div.search-group#selected").append(
                    $.parseHTML(createSearchGroupInput(fieldId)));
            if(fieldId.slice(0, 4) == "date")
                $(".search-group#selected ." + fieldId).datepicker();
        }
        else
            $("div.search-group#selected #" + fieldId).remove()
    });
}());

/*
 * Return an HTML string representing a new input field div in a search group.
 *
 * @param fieldId The id of the input field div, and its child elements.
 */
function createSearchGroupInput(fieldId){
    return [
        "<div id='" + fieldId + "'>",
            "<div class='name'>" + fieldId.replace(/-/g, " ") + "</div>",
            "<input class='" + fieldId + "' name='" + fieldId + "'type='text'>",
            "<input type='checkbox' name='regex'><span>Regex</span>",
        "</div>"
    ].join("");
}

/*
 * Create a query from advanced-search groups.
 */
function assembleQuery(){
    var groups = searchGroups.children(".search-group");
    var groupQueries = [];

    for(var group = 0; group < groups.length; group++){
        var inputFields = groups[group].querySelectorAll("input[type=text]");
        var regexCheckbox = groups[group].querySelectorAll("input[name=regex]");
        var groupQuery = [];

        for(var field = 0; field < inputFields.length; field++)
            if(inputFields[field].value.length > 0)
                groupQuery.push(genFieldQueryString(
                        inputFields[field], regexCheckbox[field].checked));

        groupQueries.push(groupQuery.join(" AND "));
    }

    console.log(groupQueries.join(" OR "));
}

/*
 * Generate a processed query string for an input field's value.
 *
 * @param field (DOM element) An `input[type=text]` element.
 * @param hasRegex (boolean) Whether or not the field's value has regex.
 */
function genFieldQueryString(field, hasRegex){
    var terms = field.value.replace(/\\/g, "\\\\").replace(/\"/g, "\\\"");
    var query = field.getAttribute("name") + ":" + ((hasRegex)?"re:":"") + terms;
    if(field.value.indexOf('"') >= 0){
        // ['"', field.getAttribute("name"), ":", regex?"re:":"", terms, '"']
        return '"' + query + '"';
    }
    return query;
}

(function testQueryStringGeneration(){
    var sampleStrings = [
        "A B",
        "A \\ B",
        '"A \\" B"',
        '"A \\" B" C D "A B"',
    ];
    for(var string = 0; string < sampleStrings.length; string++)
        console.log([
                (sampleStrings[string] + "          ").slice(0, 12),
                ":",
                "  " + genFieldQueryString($("<input>").val(sampleStrings[string])[0])
            ].join(""));
})();
