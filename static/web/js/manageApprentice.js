/**
 * Created by funing on 2018/6/1.
 */
$(function(){
    $("#manageApprentice_dg").datagrid({
        fit: true,
        rownumbers : true,
        pagination : true,
        fitColumns:true,
        singleSelect:false,
        onClickCell: onClickCell,
        pageList : [ 20 ],
        pageSize: 20,
        idField : 'id',
        columns:[
            [{
                field: 'choose',
                align: 'center',
                checkbox: true
            },{
                field: 'id',
                title: '用户ID',
                align: 'center'
            },
            //{
            //    field: 'master_id',
            //    title: '师父ID',
            //    align: 'center'
            //},
            {
                field: 'age',
                title: '年龄',
                align: 'center'
            },
            {
                field: 'gender',
                title: '性别',
                align: 'center'
            },
            {
                field: 'create_date',
                title: '注册时间',
                align: 'center'
            },
            {
                field: 'phone',
                title: '手机号',
                align: 'center'
            },
            {
                field: 'wangwang',
                title: '旺旺号',
                align: 'center'
            },
            {
                field: 'wechat_id',
                title: '微信号',
                align: 'center'
            },
            {
                field: 'blacklist',
                title: '状态',
                align: 'center'
            },
            {
                field: 'mission_interval',
                title: '任务时间间隔',
                align: 'center',
                formatter: function(value,row,index){
                    if(row.blacklist == "正常")
                        return '<span style="color: red">'+row.mission_interval+'</span>';
                    else
                        return '<span>'+row.mission_interval+'</span>';
                },
                editor: {
                    type: 'validatebox',
                    options:{
                        required: true,
                        missingMessage:'请填写任务间隔'
                    }
                }
            },
            {
                field: 'extra',
                title: '备注',
                align: 'center',
                formatter: function(value,row,index){
                    if(row.blacklist == "正常")
                        return '<span style="color: red">'+row.extra+'</span>';
                    else
                        return '<span>'+row.extra+'</span>';
                },
                editor: {
                    type: 'validatebox'
                }
            },
            {
                field: 'operate',
                title: '操作',
                align: 'center',
                formatter: function(value,row,index){
                    if(row.blacklist == "正常")
                        return '<button onclick="blackList(\''+row.wechat_id+'\')">拉黑</button> | <button onclick="beMaster(\''+row.wechat_id+'\')">升级</button> | <button onclick="saveInfo(\''+row.wechat_id+'\',\''+row.mission_interval+'\',\''+row.extra+'\')">保存</button>';
                    else if(row.blacklist == "被拉黑")
                        return '<button onclick="cancelBlack(\''+row.id+'\')">取消拉黑</button>';
                }
            }]
        ],
        toolbar: "#tips"
    });
    $('#manageApprentice_dg').datagrid('getPager').pagination({
        displayMsg:'当前显示第 {from}-{to} 条记录 ， 共 {total} 条记录',
        onSelectPage:function(pageNumber){
            getApprenticeList(pageNumber-1);
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
    if ($('#manageApprentice_dg').datagrid('validateRow', editIndex)){
        $('#manageApprentice_dg').datagrid('endEdit', editIndex);
        editIndex = undefined;
        return true;
    } else {
        return false;
    }
}
function onClickCell(index, field){
    var rows = $("#manageApprentice_dg").datagrid('getRows');
    var row = rows[index];
    if(row.blacklist == "正常")
    {
        if (endEditing()){
            $('#manageApprentice_dg').datagrid('selectRow', index)
                .datagrid('editCell', {index:index,field:field});
            editIndex = index;
        }
    }
}
//获取徒弟列表
function getApprenticeList(pageNum)
{
    var extra = $('#sift_extra').val();
    if(pageNum == null)
        pageNum = 0;
    var data = {};
    data["code"] = 24;
    data["page"] = pageNum;
    data["seller_username"] = window.localStorage.getItem("username");
    data['master']=0;
    if(extra != "")
    {
        data["extra"] = extra;
    }
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
                    if(res.data[i].role == "徒弟")
                    {
                        row.push(res.data[i]);
                    }
                    $("#manageApprentice_dg").datagrid('loadData',{ total: count['0'], rows: row });
                }
            }
        }
    })
}
//拉黑
function blackList(username)
{
    var data = {};
    data["code"] = 22;
    data["wechat_id"] = username;
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
                alert("拉黑成功");
                var page = $("#manageApprentice_dg").datagrid('getPager').data("pagination").options.pageNumber;
                getApprenticeList(page-1);
            }
            else
            {
                alert("请求失败，请重试");
            }
        }
    })
}

//取消拉黑
function cancelBlack(username)
{
    var data = {};
    data["code"] = 5;
    data["username"] = username;
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
                alert("还原成功");
                var page = $("#manageMaster_dg").datagrid('getPager').data("pagination").options.pageNumber;
                getApprenticeList(page-1);
            }
            else
            {
                alert("请求失败，请重试");
                var page = $("#manageMaster_dg").datagrid('getPager').data("pagination").options.pageNumber;
                getApprenticeList(page-1);
            }
        }
    })
}

//升级
function beMaster(username)
{
    var data = {};
    data["code"] = 26;
    data["wechat_id"] = username;
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
                var page = $("#manageApprentice_dg").datagrid('getPager').data("pagination").options.pageNumber;
                getApprenticeList(page-1);
            }
            else
            {
                alert("请求失败，请重试");
            }
        }
    })
}
var signal = false;
function saveDay()
{
    var rowData = $("#manageApprentice_dg").datagrid('getSelections');
    var day = $("#day").val();
    var signal = false;
    for(var i=0;i<rowData.length;i++)
    {
        var username = rowData[i].wechat_id;
        var extra = rowData[i].mission_interval;
        saveInfo(username,day,extra,"1");
    }
    if(signal == true){
        alert("保存成功");
        var page = $("#manageApprentice_dg").datagrid('getPager').data("pagination").options.pageNumber;
        getApprenticeList(page-1);
        $("#day").val("");
    }

}
//保存
function saveInfo(username,day,extra,sig)
{
    var data = {};
    data["code"] = 1;
    data["wechat_id"] = username;
    data["mission_interval"] = day;
    data["extra"] = extra;
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
                if(sig == null) alert("保存成功");
                else signal = true;
                var page = $("#manageMaster_dg").datagrid('getPager').data("pagination").options.pageNumber;
                getApprenticeList(page-1);
            }
            else{
                if(sig == null) alert("保存失败");
                var page = $("#manageMaster_dg").datagrid('getPager').data("pagination").options.pageNumber;
                getApprenticeList(page-1);
            }
        }
    });
}