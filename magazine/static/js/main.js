$(document).ready(function(){
    $(".photoset").colorbox({
        rel: 'photoset', 
        transition: "fade",
        speed: 300,
        scalePhotos: true,
        maxWidth: 1000,
        maxHeight: 650,
        current: '{current}/{total}',
        fadeOut: 300,
        opacity: 0.8,
        });
    $(".youtube").colorbox({iframe:true, innerWidth:640, innerHeight:390});
});
