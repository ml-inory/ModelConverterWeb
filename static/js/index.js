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

// 检查输入文件
function check_input_files() {
    var err_msg = "";
    var input_format = document.querySelector('input[name="input_format"]:checked').value;
    if (input_format == "mmdet") {
        var mmdet_config = document.getElementById("mmdet_config_name").innerHTML;
        if (mmdet_config == "") {
            err_msg = "未选择配置文件"
            return err_msg;
        }
        var mmdet_pth = document.getElementById("mmdet_pth_name").innerHTML;
        if (mmdet_pth == "") {
            err_msg = "未选择权重文件"
            return err_msg;
        }
    } else if (input_format == "mmcls") {
        var mmcls_config = document.getElementById("mmcls_config_name").innerHTML;
        if (mmcls_config == "") {
            err_msg = "未选择配置文件"
            return err_msg;
        }
        var mmcls_pth = document.getElementById("mmcls_pth_name").innerHTML;
        if (mmcls_pth == "") {
            err_msg = "未选择权重文件"
            return err_msg;
        }
    } else if (input_format == "onnx") {
        var onnx_file = document.getElementById("onnx_file_name").innerHTML;
        if (onnx_file == "") {
            err_msg = "未选择onnx输入文件"
            return err_msg;
        }
    }
    return err_msg;
}

// 检查输出名称
function check_output_name() {
    var err_msg = "";
    var output_name = document.getElementById("output_name").value;
    if (output_name == "") {
        err_msg = "未填写输出名称";
    }
    return err_msg;
}

// 检查转换参数
function check_convert_params() {
    var err_msg = "";
    // 检查输入尺寸
    var input_width = document.getElementById("input_width").value;
    var input_height = document.getElementById("input_height").value;
    if (input_width == "") {
        err_msg = "未填写输入宽度";
        return err_msg;
    }
    if (input_height == "") {
        err_msg = "未填写输入高度";
        return err_msg;
    }
    var output_format = document.querySelector('input[name="output_format"]:checked').value;
    if (output_format == "nnie") {
        // 检查RGB Order
        var rgb_order = document.getElementById("rgb_order").value;
        if (rgb_order == "") {
            err_msg = "未选择RGB Order";
            return err_msg;
        }

        // 检查mean scale
        var mean = document.getElementById("nnie_mean").value;
        var scale = document.getElementById("nnie_scale").value;
        if (mean == "") {
            err_msg = "未设置mean值";
            return err_msg;
        }
        if (scale == "") {
            err_msg = "未设置scale值";
            return err_msg;
        }

        // 检查image list
        var img_list = document.getElementById("img_list").value;
        if (img_list == "") {
            err_msg = "未设置image list";
            return err_msg;
        }
    }
    return err_msg;
}

function check_params() {
    var err_msg = "";
    // 检查输入文件
    err_msg = check_input_files();
    if (err_msg != "") {
        alert(err_msg);
        return false;
    }

    // 检查输出名称
    err_msg = check_output_name();
    if (err_msg != "") {
        alert(err_msg);
        return false;0
    }

    // 检查转换参数
    err_msg = check_convert_params();
    if (err_msg != "") {
        alert(err_msg);
        return false;0
    }

    return true;
}

function convert() {
    if (check_params()) {
        document.getElementById("convert_param_form").submit();
    }
}