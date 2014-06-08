var lastVertPos = $(window).scrollTop();

function parallax(){
    var currVertPos = $(window).scrollTop();
    var delta = currVertPos - lastVertPos;
    $(".bg").each(function(){
        $(this).css("top", parseFloat($(this).css("top")) -
            delta * $(this).attr("speed") + "px");
    });
    lastVertPos = currVertPos;
}

$(window).scroll(function(e){
    parallax();
});
