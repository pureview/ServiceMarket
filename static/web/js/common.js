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

$(function(){
    var username = window.getCookie("username");
    if(username == null)
    {
        parent.window.location.href = htmlPath + "/static/web/html/login.html";
    }
});


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
            //tools: '#tool'
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

function change(datetime)
{

    var y = datetime.toString().slice(0,4);
    var m = datetime.toString().slice(4,6);
    var d = datetime.toString().slice(6,8);
    var h = datetime.toString().slice(9,11);
    var n = datetime.toString().slice(11);
    return y+"-"+m+"-"+d+" "+h+":"+n;
}

//获取筛选时间
function getTodayTime(time)
{
    //if(time == "") {
    //    time = new Date();
    //}
    //else{
    //    time = new Date(time);
    //}
    time = new Date(time);
    var y = time.getFullYear();
    var m = time.getMonth()+1;
    var d = time.getDate();
    return y+(m<10?('0'+m):m)+(d<10?('0'+d):d)+"-0000";
}
function getNextTime(time)
{
    if(time == "") {
        time = new Date();
        time = new Date(time.setDate(time.getDate()+1));
    }
    else{
        time = new Date(time);
    }
    var y = time.getFullYear();
    var m = time.getMonth()+1;
    var d = time.getDate();
    return y+(m<10?('0'+m):m)+(d<10?('0'+d):d)+"-0000";
}

function freshTab(){
    //获得当前选中的tab
    var tab = $("#tabs").tabs("getSelected");
    //获得当前选中的tab 的href
    var url = $($(tab.panel("options"))[0].content).attr("src");
    tab.panel("refresh", url);
}

function getCookie(name)
{
    var arr,reg=new RegExp("(^| )"+name+"=([^;]*)(;|$)");

    if(arr=document.cookie.match(reg))

        return unescape(arr[2]);
    else
        return null;
}
//function siftExtraMaster(){
//// 根据备注筛选
//var extra=$('#sift_extra').value;
//// 清空数据
//$("#manageMaster_dg").datagrid('loadData',{ total: 0, rows:[] });
//if(pageNum == null)
//    pageNum = 0;
//    var data = {};
//    data["code"] = 24;
//    data["page"] = pageNum;
//    data['extra']=extra;
//    data['master']=1;
//    data["seller_username"] = window.localStorage.getItem("username");
//    $.ajax({
//        url: url,
//        type: 'post',
//        data: data,
//        success: function(res){
//            res = JSON.parse(res);
//            console.log(res);
//            if(res.code == "0")
//            {
//                var row = [];
//                var count = res.count[0];
//                for(var i=0;i<res.data.length;i++)
//                {
//                    row.push(res.data[i]);
//                    $("#manageMaster_dg").datagrid('loadData',{ total: count['0'], rows: row });
//                }
//            }
//        }
//    })
//
//}
//
//function siftExtraApprentice(){
//// 根据备注筛选
//var extra=$('#sift_extra').value;
//// 清空数据
//$("#manageApprentice_dg").datagrid('loadData',{ total: 0, rows:[] });
//if(pageNum == null)
//    pageNum = 0;
//    var data = {};
//    data["code"] = 24;
//    data["page"] = pageNum;
//    data['extra']=extra;
//    data['master']=0;
//    data["seller_username"] = window.localStorage.getItem("username");
//    $.ajax({
//        url: url,
//        type: 'post',
//        data: data,
//        success: function(res){
//            res = JSON.parse(res);
//            console.log(res);
//            if(res.code == "0")
//            {
//                var row = [];
//                var count = res.count[0];
//                for(var i=0;i<res.data.length;i++)
//                {
//                    row.push(res.data[i]);
//                    $("#manageApprentice_dg").datagrid('loadData',{ total: count['0'], rows: row });
//                }
//            }
//        }
//    })
//
//}
