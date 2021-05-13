

function history_show() {
    var history = document.getElementById("history")
    var btn = document.getElementById("history_show_btn")
    // alert(history.offsetWidth);
    if (history.style['display'] == "none") {
        history.style['display'] = "block"
        btn.innerText = ">>"
    } else {
        history.style['display'] = "none"
        btn.innerText = "<<"
    }
}