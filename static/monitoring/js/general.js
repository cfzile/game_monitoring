$("#close_errors").on("click",function () {
    $(".errors").css("display", "none");
});

$(".top_profile").on("click",function () {
    if ($(".top_profile_menu").css("display") == "none"){
        $(".top_profile_menu").css("display", "inline-block");
        // $(".top_profile").css("background", "white");
        // $("#top_profile_name").css("color", "#0D0D0D");
    }else{
        $(".top_profile_menu").css("display", "none");
        // $(".top_profile").css("background", "#0D0D0D");
        // $("#top_profile_name").css("color", "white");
    }
});
