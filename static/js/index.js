// 输入格式：单选按钮ID
var inputRadioIDArr = new Array("radio_input_mmdet", "radio_input_mmcls", "radio_input_onnx");
// 输入格式：上传按钮组合ID
var inputDivIDArr = new Array("input_mmdet", "input_mmcls", "input_onnx");

var supportInputFormat = new Array("mmdet", "mmcls", "onnx");
var supportOutputFormat = new Array("nnie", "tengine", "onnx");

// 设置输入格式radio
function set_input_format(input_format = "mmdet") {
    if (input_format == "")
        input_format = "mmdet";
    var radio_name = "radio_input_" + input_format;
    var radio = document.getElementById(radio_name);
    if (radio) {
        radio.checked = true;
    }

    // 显示对应的按钮
    for (var i = 0; i < supportInputFormat.length; i++) {
        var input_div = document.getElementById("input_" + supportInputFormat[i]);
        if (supportInputFormat[i] == input_format) {
            input_div.style["display"] = "block";
        } else {
            input_div.style["display"] = "none";
        }
    }
}

function set_output_format(output_format = "nnie") {
    if (output_format == "")
        output_format = "nnie";
    var radio = document.getElementById("radio_output_" + output_format);
    if (radio) {
        radio.checked = true;
    }

    // 显示对应的转换参数
    for (var i = 0; i < supportOutputFormat.length; i++) {
        var param_div = document.getElementById("param_" + supportOutputFormat[i]);
        if (supportOutputFormat[i] == output_format) {
            param_div.style["display"] = "block";
        } else {
            param_div.style["display"] = "none";
        }
    }


}