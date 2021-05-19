// 输入格式：单选按钮ID
var inputRadioIDArr = new Array("radio_mmdet", "radio_mmcls", "radio_onnx");
// 输入格式：上传按钮组合ID
var inputDivIDArr = new Array("input_mmdet", "input_mmcls", "input_onnx");

// 根据输入格式设置文件选择div
function select_input_format() {
    for (var i = 0; i < inputRadioIDArr.length; i++) {
        var radio = document.getElementById(inputRadioIDArr[i]);
        if (radio.checked) {
            for (var k = 0; k < inputDivIDArr.length; k++) {
                var input_div = document.getElementById(inputDivIDArr[k]);
                if (k == i) {
                    input_div.style["display"] = "block";
                } else {
                    input_div.style["display"] = "none";
                }
            }
        }
    }
}

// 设置输入格式radio
function set_input_format(input_format) {
    var radio = null;
    if (input_format == "mmdet") {
        radio = document.getElementById(inputRadioIDArr[0]);
    }
    else if (input_format == "mmcls") {
        radio = document.getElementById(inputRadioIDArr[1]);
    }
    else if (input_format == "onnx") {
        radio = document.getElementById(inputRadioIDArr[2]);
    }
    console.log(input_format)
    if (radio) {
        radio.checked = true;
    }
    select_input_format();
}