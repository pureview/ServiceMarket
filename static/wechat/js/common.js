/**
 * Created by funing on 2018/6/3.
 */
var basePath;
var url;
var htmlPath;
//接口地址
basePath = window.location.protocol+"//"+window.location.host+":8080";
url=basePath+"/mission";
htmlPath = window.location.protocol+"//"+window.location.host+":80";
//basePath = "http://taobaoshare.cn/";
//url = "http://taobaoshare.cn:8080/mission";

function getQueryString(name) {
    var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
    var r = window.location.search.substr(1).match(reg);

    if (r != null) {
        return unescape(r[2]);
    }
    return null;
}

//注册获取图片后显示
function show(f) {
    var str = "";
    for (var i = 0; i < f.length; i++) {
        var reader = new FileReader();
        reader.readAsDataURL(f[i]);
        reader.onload = function (e) {
            str += "<img width='70' height='70' id='img' src='" + e.target.result + "'/>";
            $("#img")[0].outerHTML = str;
        }
    }
    $("#uploadImg").css("display","none");
}

function getTips()
{
    var data ={};
    data["code"]="33";
    data["op"] = "0";
    data["seller_username"] = window.localStorage.getItem("seller_username");
    console.log(data);
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            console.log(res);
            if(res.code == 0)
            {
                $("#tips").text(res.data);
            }
        }
    })
}
//刷新获取任务
function refresh()
{
    var data = {};
    data["code"] = 39;
    data["wechat_id"] = window.localStorage.getItem("openID");
    data["seller_username"] = window.localStorage.getItem("seller_username");
    console.log(data);
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            console.log(res);
            if(res.message == "申请任务")
                $("#msg").text("您获取一个任务，请“点我”进行任务");
            else
                $("#msg").text(res.message);
        }
    });
}

function changeTime(datetime)
{

    var y = datetime.slice(0,4);
    var m = datetime.slice(4,6);
    var d = datetime.slice(6,8);
    var h = datetime.slice(9,11);
    var n = datetime.slice(11);
    return y+"-"+m+"-"+d+" "+h+":"+n;
}

