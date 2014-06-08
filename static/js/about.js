var lastVertPos = $(window).scrollTop();

function parallax(){
    var currVertPos = $(window).scrollTop();
    var delta = currVertPos - lastVertPos;
    $(".bg").each(function(){
        $(this).css("top", parseFloat($(this).css("top")) - delta * 1.35 + "px");
    });
    $(".bg#img-1").each(function(){
        console.log($(this).css("top"));
    });
    lastVertPos = currVertPos;
}

$(window).scroll(function(e){
    parallax();
});
