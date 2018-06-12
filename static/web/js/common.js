/**
 * Created by funing on 2018/5/30.
 */
var basePath;
var url;
var htmlPath;

//接口地址
basePath = window.location.protocol+"//"+window.location.host+":8080";
url=basePath+"/mission";
htmlPath = window.location.protocol+"//"+window.location.host+":80";
//url="http://taobaoshare.cn:8080/mission";

//用户登录
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
            }
            else{
                alert("登录失败");
            }
        }
    })
}
//忘记密码
function forgetPWD(username)
{

}


//在右侧打开tab选项
function openTab(title,id,url)
{
    // 对选择样式进行处理
    $("li").removeClass('background');
    $("#"+id).addClass('background');
    // 创建tab标签
    var content = '<iframe scrolling="auto" frameborder="0" data-options="closable:true"  src="'+url+'" style="width:100%;height:100%;"></iframe>';
    // 判断tab标签是否存在
    if ($("#tabs").tabs('exists', title))
    {
        $('#tabs').tabs('select', title);
    } else {
        $('#tabs').tabs('add', {
            title : title,
            closable : true,
            content : content
        });
    }
}

function changeTime(datetime)
{
    datetime= new Date(Date.parse(datetime));
    var y = datetime.getFullYear();
    var m = datetime.getMonth()+1;//js从0开始取
    var d = datetime.getDate();
    var h = datetime.getHours();
    var n = datetime.getMinutes();
    return y+(m<10?('0'+m):m)+(d<10?('0'+d):d)+'-'+(h<10?('0'+h):h)+(n<10?('0'+n):n);
}