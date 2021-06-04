// 输入格式：单选按钮ID
var inputRadioIDArr = new Array("radio_input_mmdet", "radio_input_mmcls", "radio_input_onnx");
// 输入格式：上传按钮组合ID
var inputDivIDArr = new Array("input_mmdet", "input_mmcls", "input_onnx");

var supportInputFormat = new Array("mmdet", "mmcls", "onnx");
var supportOutputFormat = new Array("nnie", "tengine", "onnx");
var base_url = "/api/v1";
var username;
var access_token;  
var refresh_token;
var tasks = null;

$(document).ready(function() {
    
    $.ajax({
        url: base_url + "/session",
        type: "GET",
        dataType: "json",
        success: function(response) {
            sessionStorage.setItem("access_token", response.access_token);
            sessionStorage.setItem("refresh_token", response.refresh_token);
            sessionStorage.setItem("username", response.username);
        }
    });
    username = sessionStorage.getItem("username");
    access_token = sessionStorage.getItem("access_token");  
    refresh_token = sessionStorage.getItem("refresh_token");
    
    // 刷新token
    // $.ajax({
    //     url: base_url + "/token",
    //     type: "GET",
    //     dataType: "json",
    //     beforeSend: function (xhr) {
    //         xhr.setRequestHeader('Authorization', 'Bearer ' + refresh_token);
    //     },
    //     success: function(response) {
    //         access_token = response.access_token;
    //         sessionStorage.setItem("access_token", access_token);  
    //     }
    // });
    // access_token = sessionStorage.getItem("access_token");  

    // 获取任务
    get_tasks();

    // 设置输入格式radio
    $("input[name='input_format']").click(function() {
        var on_radio = $(this).val();
        $("div.input_upload").hide();
        $("#input_" + on_radio).show();
    });

    // 设置输出格式radio
    $("input[name='output_format']").click(function() {
        var on_radio = $(this).val();
        $("div.convert_param").hide();
        $("#param_" + on_radio).show();
    });

    // 登出
    $("#logout_btn").click(function() {
        $.ajax({
            url: base_url + "/logout",
            type: "POST",
            cache: false,
            data: {
                "username": username
            },
            contentType: "x-www-form-urlencoded",
            dataType: "json",
            beforeSend: function (xhr) {
                xhr.setRequestHeader('Authorization', 'Bearer ' + access_token);
            },
            success: function(response) {
                window.location.href = "/login";
            }
        });
    });

    // 转换
    $("#convert_btn").click(function() {
        var input_form = get_input_form();
        var convert_form = get_convert_form();

        // POST 输入
        var input_xhr = $.ajax({
            url: base_url + "/input",
            type: "POST",
            data: input_form,
            dataType: "json",
            processData: false,
            contentType: false,
            beforeSend: function (xhr) {
                xhr.setRequestHeader('Authorization', 'Bearer ' + access_token);
            },
            error: function(response) {
                let msg = response.responseJSON.msg;
                alert(msg);
            }
        });

        // POST 转换
        input_xhr.success(function() {
            $.ajax({
                url: base_url + "/convert",
                type: "POST",
                data: convert_form,
                dataType: "json",
                processData: false,
                contentType: false,
                beforeSend: function (xhr) {
                    xhr.setRequestHeader('Authorization', 'Bearer ' + access_token);
                },
                success: function(response) {
                    get_tasks();
                    // var tb = document.getElementById("tasks_tb");
                    // var row = tb.insertRow();
                    // var date_cell = row.insertCell();
                    // var format_cell = row.insertCell();
                    // var output_cell = row.insertCell();
                    // date_cell.innerHTML = response.date;
                    // format_cell.innerHTML = response.output_format;
                    // output_cell.innerHTML = response.output_name;
    
                },
                error: function(response) {
                    let msg = response.responseJSON.msg;
                    alert(msg);
                }
            });
        });
    });

    setInterval(get_tasks, 5000);
});

function get_input_form()
{
    var form = new FormData();
    var input_format = document.querySelector('input[name="input_format"]:checked').value;
    // console.log("input_format: " + input_format);

    var input_config = "";
    var input_config_elem = document.getElementById(input_format + "_config");
    if (input_config_elem != null)
    {
        input_config = input_config_elem.files[0];
    }
    var input_weight = "";
    var input_weight_elem = document.getElementById(input_format + "_weight");
    if (input_weight_elem != null)
    {
        input_weight = input_weight_elem.files[0];
    }

    form.append("format", input_format);
    form.append("config", input_config);
    form.append("weight", input_weight);
    return form;
}

function get_convert_form()
{
    var form = new FormData();
    var width = document.getElementById("input_width").value;
    if (width == "")    width = "-1";
    var height = document.getElementById("input_height").value;
    if (height == "")   height = "-1";
    var order = document.getElementById("rgb_order").value;
    var mean = document.getElementById("nnie_mean").value;
    var scale = document.getElementById("nnie_scale").value;
    var img_archive = document.getElementById("img_archive").files[0];
    var output_format = document.querySelector('input[name="output_format"]:checked').value;
    var output_name = document.getElementById("output_name").value;

    form.append("width", width);
    form.append("height", height);
    form.append("order", order);
    form.append("mean", mean);
    form.append("scale", scale);
    form.append("output_format", output_format);
    form.append("output_name", output_name);
    form.append("img_archive", img_archive);
    return form;
}

// 获取时间
function get_date() {
    var str = "";
    var d = new Date();
    var year = d.getFullYear();
    var month = d.getMonth() + 1;
    var day = d.getDate();
    var hour = d.getHours();
    var minute = d.getMinutes();
    var second = d.getSeconds();
    str = year + "/" + month + "/" + day + " " + hour + ":" + minute + ":" + second;
    return str;
}

// 获取任务
function get_tasks() {
    $.ajax({
        url: base_url + "/tasks", 
        type: "GET",
        dataType: "json",
        beforeSend: function (xhr) {
            xhr.setRequestHeader('Authorization', 'Bearer ' + access_token);
        },
        success: function(response) {
            // Now that we've completed the request schedule the next one.
            var tb_len = response.tasks.length;
            console.log("table len: " + tb_len);
            if (tb_len > 0)
            {
                var tb = document.getElementById("tasks_tb");
                var tasks = response.tasks;
                for (var i = 0; i < tb_len; i++)
                {
                    var row = tb.rows.item(i+1);
                    if (row == null)
                    {
                        row = tb.insertRow();
                        row.insertCell();
                        row.insertCell();
                        row.insertCell();
                    }
                    var date_cell = row.cells[0];
                    var format_cell = row.cells[1];
                    var output_cell = row.cells[2];
                    date_cell.innerHTML = tasks[i].date;
                    format_cell.innerHTML = tasks[i].output_format;
                    output_cell.innerHTML = tasks[i].output_name;
                    if (tasks[i].success)
                    {
                        output_cell.innerHTML = "<a href='/download/" + i + "'>" + tasks[i].output_name + "</a>";
                    }
                    else
                    {
                        
                    }
                }
                
            }
        }
  });
}