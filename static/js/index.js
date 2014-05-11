var typingTimer;
var finishedTypingInterval = 650;

searchBar = document.querySelectorAll("form#search-bar input[type='text']")[0]
console.log(searchBar)

searchBar.onkeyup = function(){
    clearTimeout(typingTimer);
    if(searchBar.value){
        typingTimer = setTimeout(finishedTyping, doneTypingInterval);
    }
};

function finishedTyping(){
    console.log("You stopped typing.");
}
