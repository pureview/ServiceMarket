/**
 * Created by funing on 2018/6/17.
 */
//用户登录
var basePath;
var url;
var htmlPath;

//接口地址
basePath = window.location.protocol+"//"+window.location.host+":8080";
url=basePath+"/mission";
htmlPath = window.location.protocol+"//"+window.location.host+":80";
//url="http://taobaoshare.cn:8080/mission";

function login()
{
    var username = $("#username").val();
    var password = $("#password").val();
    var data = {};
    data["code"] = "28";
    data["seller_username"]=username;
    data["passwd"] = password;
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            if(res.code == '0')
            {
                window.location.href="index.html";
                window.localStorage.setItem("username",username);
                window.localStorage.setItem("password",password);
                window.setCookie("username",username,"d1");
            }
            else{
                alert("登录失败");
            }
        }
    })
}

//设置cookie
function setCookie(name,value,time)
{
    var strsec = getsec(time);
    var exp = new Date();
    exp.setTime(exp.getTime() + strsec*1);
    document.cookie = name + "="+ escape (value) + ";expires=" + exp.toGMTString();
}
function getsec(str)
{
    var str1=str.substring(1,str.length)*1;
    var str2=str.substring(0,1);
    if (str2=="s")
    {
        return str1*1000;
    }
    else if (str2=="h")
    {
        return str1*60*60*1000;
    }
    else if (str2=="d")
    {
        return str1*24*60*60*1000;
    }
}