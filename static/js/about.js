/*
 * @file Implements a parallax effect on the about page.
 */

var lastVertPos = $(window).scrollTop();

$(window).scroll(function(e){
    var currVertPos = $(window).scrollTop();
    var delta = currVertPos - lastVertPos;
    $(".bg").each(function(){
        $(this).css("top", parseFloat($(this).css("top")) -
            delta * $(this).attr("speed") + "px");
    });
    lastVertPos = currVertPos;
});
