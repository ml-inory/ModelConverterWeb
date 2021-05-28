function submit_login(){
    $("#login_btn").on("click", function (e){
        e.preventDefault();
    });
    $.post("/api/v1/login",
        $("#login_form").serialize(),
        function (response) {
                window.location.href = "/";
        },
        "json"
    )
        .error(function (response) {
            let msg = $.parseJSON(response.responseText).msg;
            alert(msg);
        });
}