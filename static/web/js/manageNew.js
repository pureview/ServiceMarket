/**
 * Created by funing on 2018/6/1.
 */
$(function(){
    $("#manageNew_dg").datagrid({
        fit: true,
        rownumbers : true,
        pagination : true,
        fitColumns:true,
        singleSelect:false,
        onClickCell: onClickCell,
        pageList : [ 20 ],
        pageSize : 20,
        idField : 'id',
        columns:[
            [{
                field: 'inviter_id',
                title: '介绍人ID',
                align: 'center'
            },
            {
                field: 'gender',
                title: '性别',
                align: 'center'
            },
            {
                field: 'age',
                title: '年龄',
                align: 'center'
            },
            {
                field: 'trading_image',
                title: '交易图片',
                align: 'center',
                formatter: function(value,row,index){
                    return '<a onclick="openImgWindow(\''+row.trading_image+'\')">交易图片</a>';
                }
            },
            {
                field: 'role',
                title: '状态',
                align: 'center'
            },
            {
                field: 'extra',
                title: '备注',
                align: 'center'
            },
            {
                field: 'operate',
                title: '操作',
                align: 'center',
                formatter: function(value,row,index){
                    if(row.role == "审核中" || row.role == "师傅审核完毕")
                        return '<a onclick="agree(\''+row.wechat_id+'\')">通过</a> | <a onclick="disagree(\''+row.wechat_id+'\')">拒绝</a> | <a onclick="newToMaster(\''+row.wechat_id+'\')">升级为师傅</a>';
                    else if(row.role == "卖家审核完毕")
                        return '<a onclick="newToMaster(\''+row.wechat_id+'\')">升级为师傅</a>';
                }
            }]
        ],
        toolbar: [
            {

            }
        ]
    });
    $('#manageNew_dg').datagrid('getPager').pagination({
        displayMsg:'当前显示第 {from}-{to} 条记录 ， 共 {total} 条记录',
        onSelectPage:function(pageNumber){
            getNewList(pageNumber-1);
        }
    });
});
$.extend($.fn.datagrid.methods, {
    editCell: function(jq,param){
        return jq.each(function(){
            var opts = $(this).datagrid('options');
            var fields = $(this).datagrid('getColumnFields',true).concat($(this).datagrid('getColumnFields'));
            for(var i=0; i<fields.length; i++){
                var col = $(this).datagrid('getColumnOption', fields[i]);
                col.editor1 = col.editor;
                if (fields[i] != param.field){
                    col.editor = null;
                }
            }
            $(this).datagrid('beginEdit', param.index);
            for(var i=0; i<fields.length; i++){
                var col = $(this).datagrid('getColumnOption', fields[i]);
                col.editor = col.editor1;
            }
        });
    }
});
var editIndex = undefined;
function endEditing(){
    if (editIndex == undefined){return true}
    if ($('#setupShop_dg').datagrid('validateRow', editIndex)){
        $('#setupShop_dg').datagrid('endEdit', editIndex);
        editIndex = undefined;
        return true;
    } else {
        return false;
    }
}
function onClickCell(index, field){
    if (endEditing()){
        $('#manageNew_dg').datagrid('selectRow', index)
            .datagrid('editCell', {index:index,field:field});
        editIndex = index;
    }
}

//获取用户列表
function getNewList(pageNum)
{
    if(pageNum == null)
        pageNum = 0;
    var data = {};
    data["code"] = 24;
    data["page"] = pageNum;
    data["seller_username"] = window.localStorage.getItem("username");
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            console.log(res);
            if(res.code == "0")
            {
                var row = [];
                var count = res.count[0];
                for(var i=0;i<res.data.length;i++)
                {
                    if(res.data[i].role == "审核中" || res.data[i].role =="师傅审核完毕" || res.data[i].role=="卖家审核完毕")
                    {
                        row.push(res.data[i]);
                    }
                    $("#manageNew_dg").datagrid('loadData',{ total: count['0'], rows: row });
                }
            }
        }
    })
}

//审核
function agree(username)
{
    var data = {};
    data["code"] = 20;
    data["wechat_id"] = username;
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            console.log(res);
            if(res.code == "0")
            {
                alert("通过申请");
                var page = $("#manageNew_dg").datagrid('getPager').data("pagination").options.pageNumber;
                getNewList(page-1);
            }
            else
            {
                alert("请求失败，请重试");
            }
        }
    })
}

function disagree(username)
{
    var data = {};
    data["code"] = 34;
    data["wechat_id"] = username;
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            console.log(res);
            if(res.code == "0")
            {
                alert("拒绝申请");
                var page = $("#manageNew_dg").datagrid('getPager').data("pagination").options.pageNumber;
                getMasterList(page-1);
            }
            else
            {
                alert("请求失败，请重试");
            }
        }
    })
}

function openImgWindow(img)
{
    $("#newImg").window('open');
    $("#img").attr("src",htmlPath+"/"+img);
}

function newToMaster(id)
{
    var data = {};
    data["code"] = "37";
    data["wechat_id"] = id;
    data["seller_username"] = window.localStorage.getItem("username");
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            console.log(res);
            if(res.code == "0")
            {
                alert("升级成功");
                var page = $("#manageNew_dg").datagrid('getPager').data("pagination").options.pageNumber;
                getMasterList(page-1);
            }
            else
            {
                alert("请求失败，请重试");
            }
        }
    })
}