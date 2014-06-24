/*
 * @file Implements a parallax effect on the about page.
 */

var lastVertPos = $(window).scrollTop();

/*
 * Scroll `div#img-[1-4]` at a greater speed than the text, producing a
 * parallax effect.
*/
$(window).scroll(function(e){
    var currVertPos = $(window).scrollTop();
    var delta = currVertPos - lastVertPos;
    $(".bg").each(function(){
        $(this).css("top", parseFloat($(this).css("top")) -
            delta * $(this).attr("speed") + "px");
    });
    lastVertPos = currVertPos;
});

/*
 * Make the dimensions of the vimeo video fluid.
*/
(function adjustVimeoDimensions(){
    var iframe = $("iframe#vimeo")[0];
    var videoRatio = (iframe.height / iframe.width) * 100;

    iframe.style.position = "absolute";
    iframe.style.top = "0";
    iframe.style.left = "0";
    iframe.width = "100%";
    iframe.height = "100%";

    iframe.style.height = "";
    iframe.style.width = "";

    var wrap = document.createElement("div");
    wrap.className = "fluid-vids";
    wrap.style.width = "100%";
    wrap.style.position = "relative";
    wrap.style.paddingTop = videoRatio + "%";

    var iframeParent = iframe.parentNode;
    iframeParent.insertBefore(wrap, iframe);
    wrap.appendChild(iframe);
}());
