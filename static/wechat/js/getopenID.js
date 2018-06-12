/**
 * Created by funing on 2018/6/9.
 */
//var openID = "123";
//var seller_username = "test";
//var seller_id = "test";
//code = "001XReaV0LHRvV1c089V0tQ5aV0XRea5";
//seller_username = "test";
var code;
//var openID = "oWN6I06odGU-NfKEm97hQhuMjuNk";
var openID;
var seller_username;
var seller_id;

//获取用户openID
code = getQueryString("code");
seller_username = getQueryString("state");
seller_id = getQueryString("seller_id");
window.localStorage.setItem("seller_username",seller_username);
window.localStorage.setItem("seller_id",seller_id);
$(function(){
    var user_data = {};
    user_data["code"] = 27;
    user_data["wechat_code"] = code;
    user_data["seller_username"] = seller_username;
    $.ajax({
        url: url,
        type: 'POST',
        data: user_data,
        dataType:"JSON",
        success: function(res){
            if(res.code == "0")
            {
                openID = res.data;
                window.localStorage.setItem("openID",openID);
                getUserRole();
            }
        }
    })
});

//判断该用户是否注册

function getUserRole()
{
    var role_data = {};
    role_data["code"] = "18";
    role_data["wechat_id"] = window.localStorage.getItem("openID");
    role_data["seller_username"] = seller_username;
    $.ajax({
        url: url,
        type: 'POST',
        dataType:'JSON',
        data: role_data,
        success: function(res){
            if(res.code == "1")
            {
                window.location.href = htmlPath+"/static/wechat/html/newStatus.html";
            }
            else if(res.code == "0")
            {
                if(res.master == false)
                {
                    window.location.href = htmlPath+"/static/wechat/html/apprentice.html";
                }
                else
                {
                    window.location.href = htmlPath+"/static/wechat/html/master.html";
                }
            }
        }
    })

}