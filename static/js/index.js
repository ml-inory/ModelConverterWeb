// 输入格式：单选按钮ID
var inputRadioIDArr = new Array("radio_mmdet", "radio_mmcls", "radio_onnx");
// 输入格式：上传按钮组合ID
var inputDivIDArr = new Array("input_mmdet", "input_mmcls", "input_onnx");

// 选择输入格式的onclick事件
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