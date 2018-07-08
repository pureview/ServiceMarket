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
function show1(f) {
    var str = "";
    for (var i = 0; i < f.length; i++) {
        var reader = new FileReader();
        reader.readAsDataURL(f[i]);
        reader.onload = function (e) {
            str += "<img width='70' height='70' id='img' src='" + e.target.result + "'/>";
            $("#img1")[0].outerHTML = str;
        }
    }
    $("#uploadImg1").css("display","none");
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
    $("#msg").html("");
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
            if(res.code == "0")
            {
                $("#tip").text(res.message);
            }else if(res.code == "1")
            {
                var now = new Date();
                var time = res.waiting_time.toFixed(0);
                var endTime = new Date(now.setTime(now.getTime()+time*1000));
                window.localStorage.setItem("left_time",endTime);
                leftTime();
                //var time = formatSeconds(res.waiting_time);
                //$("#tip").text("距离下个任务还有"+time);

                $("#getTask").css("background","#ccc");
                $("#getTask").attr("disabled","disabled");
            }
            else if(res.code=="3"){
                $("#tip").text(res.message);
            }

            else{
                $("#tip").text(res.message);
                $("#getTask").css("background","#ccc");
                $("#getTask").attr("disabled","disabled");
            }
        }
    });
}

function leftTime() {
    var nowtime = new Date();//当前时间
    var endtime = new Date(window.localStorage.getItem("left_time"));//结束时间
    var lefttime = parseInt((endtime.getTime() - nowtime.getTime()) / 1000); // 剩余时间
    var h = parseInt((lefttime/ 60 / 60) % 60);
    var m = parseInt((lefttime / 60) % 60); // 剩余分钟数
    var s = parseInt(lefttime % 60);    // 剩余秒数

    document.getElementById("tip").innerHTML ="距离下一个任务还有" + h + "小时" + m + "分" + s + "秒";
    var ti = setTimeout(leftTime, 1000);

    if (lefttime <= 0) {
        clearTimeout(ti);
    }
}

//转换时间
function formatSeconds(value) {
    var theTime = parseInt(value);// 秒
    var theTime1 = 0;// 分
    var theTime2 = 0;// 小时
    if(theTime > 60) {
        theTime1 = parseInt(theTime/60);
        theTime = parseInt(theTime%60);
        if(theTime1 > 60) {
            theTime2 = parseInt(theTime1/60);
            theTime1 = parseInt(theTime1%60);
        }
    }
    var result = ""+parseInt(theTime)+"秒";
    if(theTime1 > 0) {
        result = ""+parseInt(theTime1)+"分"+result;
    }
    if(theTime2 > 0) {
        result = ""+parseInt(theTime2)+"小时"+result;
    }
    return result;
}
function toTaskDetail(id)
{
    window.location.href="taskDetail.html?id="+id;
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

