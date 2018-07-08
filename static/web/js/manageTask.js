/**
 * Created by funing on 2018/5/31.
 */
$(function(){
    var dg = $("#manageTask_dg").datagrid({
        fit: true,
        rownumbers : true,
        pagination : true,
        fitColumns:true,
        singleSelect:false,
        nowrap:true,
        //onClickCell: onClickCell,
        pageList : [ 20],
        pageSize: 20,
        idField : 'id',
        columns:[
            [{
                field: 'choose',
                align: 'center',
                checkbox: true
            },{
                field: 'id',
                title: '任务ID',
                align: 'center',
                formatter: function(value){
                    //toOrder(value);
                    return '<a onclick="toOrder(\''+value+'\')">'+value+'</a>';
                }
            },{
                field: 'good_name',
                title: '商品名称',
                align: 'center'
            },{
                field: 'mission_nums',
                title: '总单数',
                align: 'center'
            },{
                field: 'keywords',
                title: '关键字',
                align: 'center'
            }, {
                field: 'status',
                title: '任务状态',
                align: 'center',
                formatter: function(value,row,index){
                    if(value == 0)
                        return "已发布";
                    else if(value == 1)
                        return "已取消";
                    else if(value == 2)
                        return "已结束";
                }
            }, {
                field: 'begin_time',
                title: '开始时间',
                align: 'center',
                formatter: function(value,row,index){
                    return change(row.begin_time);
                }
            }, {
                field: 'end_time',
                title: '结束时间',
                align: 'center',
                formatter: function(value,row,index){
                    return change(row.end_time);
                }
            }, {
                field: 'operate',
                title: '操作',
                align: 'center',
                formatter: function(value,row,index){
                    if(row.status == 0)
                        return '<button onclick="cancelTask(\''+row.id+'\')">取消任务</button> | <button onclick="deleteTask(\''+row.id+'\')">删除</button>';
                    else if(row.status == 1)
                        return '<button onclick="reSetupTask(\''+row.id+'\')">重新发布</button> | <button onclick="deleteTask(\''+row.id+'\')">删除</button>';
                }
            }]
        ],
        toolbar: "#searchtool"
    });
    dg.datagrid('getPager').pagination({
        displayMsg:'当前显示第 {from}-{to} 条记录 ， 共 {total} 条记录',
        onSelectPage:function(pageNumber){
            getTaskList(pageNumber-1);
        }
    });
});
//设置时间格式
function myformatter(date){
    date= new Date(Date.parse(date));
        var y = date.getFullYear();
        var m = date.getMonth()+1;
        var d = date.getDate();
        var h = date.getHours();
        var n = date.getMinutes();
        return y+"/"+(m<10?('0'+m):m)+"/"+(d<10?('0'+d):d)+'-'+(h<10?('0'+h):h)+":"+(n<10?('0'+n):n);
    //}
}

//获取任务
function getTaskList(pageNum)
{
    var begin_time = $("#begin_date").val();
    var end_time = $("#end_date").val();
    if(pageNum == null)
        pageNum = 0;
    var data = {};
    data["code"] = 2;
    data["page"] = pageNum;
    data["seller_username"] = window.localStorage.getItem("username");
    if(begin_time != "" && end_time != "")
    {
        data["begin_time"] = getTodayTime(begin_time);
        data["end_time"] = getTodayTime(end_time);
    }
    console.log(data);
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            console.log(res);
            var count = res.count[0];
            if(res.code == "0")
            {
                var row = [];
                for(var i=0; i<res.data.length;i++)
                {
                    row.push(res.data[i]);
                }
                $("#manageTask_dg").datagrid('loadData',{ total: count['count(*)'], rows: row });
            }
        }
    })
}

//取消任务
function cancelTask(id)
{
    var data = {};
    data["code"] = 7;
    data["seller_username"] = window.localStorage.getItem("username");
    data["id"] = id;
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            console.log(res);
            if(res.code == "0")
            {
                alert("取消成功");
                var page = $("#manageTask_dg").datagrid('getPager').data("pagination").options.pageNumber;
                getTaskList(page-1);
            }
        }
    })
}

//删除任务
function deleteTask(id)
{
    var data = {};
    data["code"] = 3;
    data["seller_username"] = window.localStorage.getItem("username");
    data["id"] = id;
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            console.log(res);
            if(res.code == "0")
            {
                alert("删除成功");
                var page = $("#manageTask_dg").datagrid('getPager').data("pagination").options.pageNumber;
                getTaskList(page-1);
            }
        }
    })
}

function reSetupTask(id)
{
    window.localStorage.setItem("mission_id",id);
    $('.tabs-first', parent.document).click();
    parent.window.callReset(id);
}

function toOrder(id)
{
    window.localStorage.setItem("task_id",id);
    parent.window.callOrder(id);
}