/**
 * Created by funing on 2018/5/31.
 */
$(function(){
    var mdg = $("#manageOrder_dg").datagrid({
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
            },
            {
                field: 'mission_id',
                title: '任务ID',
                align: 'center'
            },
            {
                field: 'user_order_id',
                title: '订单ID',
                align: 'center'
            },
            {
                field: 'order_id',
                title: '淘宝订单号',
                align: 'center'
            },
            {
                field: 'wangwang',
                title: '旺旺号',
                align: 'center'
            },
            {
                field: 'username',
                title: '用户账号',
                align: 'center'
            },
            {
                field: 'shop',
                title: '店铺名',
                align: 'center'
            },
            {
                field: 'keyword',
                title: '关键词',
                align: 'center'
            },
            {
                field: 'good_name',
                title: '商品名',
                align: 'center'
            },
            {
                field: 'good_price',
                title: '商品价格',
                align: 'center',
                formatter: function(value,row,index){
                    return '<span style="color: red">'+row.good_price+'</span>';
                },
                editor: {
                    type: 'validatebox',
                    options:{
                        required: true,
                        missingMessage:'请填写商品价格'
                    }
                }
            },
            {
                field: 'begin_time',
                title: '任务发布时间',
                align: 'center',
                formatter: function(value,row,index){
                    return change(row.begin_time);
                }
            },
            {
                field: 'accept_time',
                title: '接单时间',
                align: 'center',
                formatter: function(value,row,index){
                    return change(row.accept_time);
                }
            },
            {
                field: 'order_begin_time',
                title: '订单开始时间',
                align: 'center',
                formatter: function(value,row,index){
                    return change(row.order_begin_time);
                }
            },

            {
                field: 'status',
                title: '状态',
                align: 'center'
            },
            {
                field: 'slave_money',
                title: '基本佣金',
                align: 'center'
            },
            {
                field: 'master_money',
                title: '提成佣金',
                align: 'center'
            },
            {
                field: 'operate',
                title: '操作',
                align: 'center',
                formatter: function(value,row,index){
                    if(row.status == "待审核")
                        return '<button onclick="agreeTask(\''+row.user_order_id+'\')">返现</button> | <button onclick="disagreeTask(\''+row.user_order_id+'\')">拒绝</button> | <button onclick="savePrice(\''+row.user_order_id+'\',\''+row.good_price+'\')">保存</button>';
                    else
                        return '<button onclick="savePrice(\''+row.user_order_id+'\',\''+row.good_price+'\')">保存</button>';
                }
            }]
        ],
        toolbar: "#searchtool"
    });
    $("#manageOrder_dg").datagrid('getPager').pagination({
        displayMsg:'当前显示第 {from}-{to} 条记录 ， 共 {total} 条记录',
        onSelectPage:function(pageNumber){
            getOrderList(pageNumber-1);
        }
    });
});

//设置单元格可编辑
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
    if ($('#manageOrder_dg').datagrid('validateRow', editIndex)){
        $('#manageOrder_dg').datagrid('endEdit', editIndex);
        editIndex = undefined;
        return true;
    } else {
        return false;
    }
}
function onClickCell(index, field){
    if (endEditing()) {
        $('#manageOrder_dg').datagrid('selectRow', index)
            .datagrid('editCell', {index: index, field: field});
        editIndex = index;
        }
}

//获取订单列表
function getOrderList(pageNum)
{
    var mission_id = window.localStorage.getItem("task_id");
    var begin_time = $("#begin_date").val();
    var end_time = $("#end_date").val();
    var status = $("#status").val();
    var shop =$("#shop").val();
    var good_name = $("#good_name").val();
    if(pageNum == null || pageNum == "-1")
        pageNum = 0;
    var data = {};
    data["code"] = "10";
    data["seller_username"] = window.localStorage.getItem("username");
    data["page"] = pageNum;
    if(mission_id != "null")
    {
        data["mission_id"] = mission_id;
    }
    if(status != "全部")
    {
        data["status"] = status;
    }
    if(shop != "全部")
    {
        data["shop"] = shop;
    }
    if(begin_time != "" && end_time != "")
    {
        data["begin_time"] = getTodayTime(begin_time);
        data["end_time"] = getTodayTime(end_time);
    }
    if(good_name != "")
    {
        data["good_name"] = good_name;
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
                for(var i=0;i<res.data.length;i++)
                {
                    row.push(res.data[i]);
                }
                $("#manageOrder_dg").datagrid('loadData',{ total: count['0'], rows: row });
                //window.localStorage.setItem("task_id",null);
            }
        }
    })
}

function getAllOrder()
{
    window.localStorage.setItem("task_id",null);
    getOrderList();
}

function agreeTask(id)
{
    var data ={};
    data["code"] = "19";
    data["op"] = "0";
    data["user_order_id"] = id;
    data["seller_username"] = window.localStorage.getItem("username");
    console.log(data);
    $.ajax({
        url: url,
        type:'post',
        data: data,
        success: function(res) {
            res = JSON.parse(res);
            console.log(res);
            if(res.code == "0")
            {
                var page = $("#manageOrder_dg").datagrid('getPager').data("pagination").options.pageNumber;
                getOrderList(page-1);
            }
            else
            {
                alert("申请失败");
                var page = $("#manageOrder_dg").datagrid('getPager').data("pagination").options.pageNumber;
                getOrderList(page-1);
            }
        }
    });
}

function disagreeTask(id)
{
    var data ={};
    data["code"] = "19";
    data["op"] = "1";
    data["user_order_id"] = id;
    data["seller_username"] = window.localStorage.getItem("username");
    $.ajax({
        url: url,
        type:'post',
        data: data,
        success: function(res) {
            res = JSON.parse(res);
            console.log(res);
            if(res.code == "0")
            {
                var page = $("#manageOrder_dg").datagrid('getPager').data("pagination").options.pageNumber;
                getOrderList(page-1);
            }
            else
            {
                alert("申请失败");
                var page = $("#manageOrder_dg").datagrid('getPager').data("pagination").options.pageNumber;
                getOrderList(page-1);
            }
        }
    });

}

//保存价格
function savePrice(id,price)
{
    var data = {};
    data["code"] = 47;
    data["user_order_id"] = id;
    data["good_price"] = price;
    console.log(data);
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        async: false,
        success: function(res){
            res = JSON.parse(res);
            console.log(res);
            if(res.code == "0")
            {
                alert("保存成功");
                var page = $("#manageOrder_dg").datagrid('getPager').data("pagination").options.pageNumber;
                getOrderList(page-1);
            }
            else{
                alert("保存失败");
                var page = $("#manageOrder_dg").datagrid('getPager').data("pagination").options.pageNumber;
                getOrderList(page-1);
            }
        }
    });
}

//导出excel
function dataExcel()
{
    var rowData = $("#manageOrder_dg").datagrid('getSelections');
    var id_arr = [];
    console.log(rowData);
    for(var i=0;i<rowData.length;i++)
    {
        id_arr.push(rowData[i].user_order_id);
    }
    //var begin_time = getTodayTime($("#begin_date").val());
    //var end_time = getNextTime($("#end_date").val());
    //console.log(begin_time);
    //console.log(end_time);
    var data = {};
    data["code"] = "38";
    data["seller_username"] = window.localStorage.getItem("username");
    data["user_order_ids"] = id_arr.join(" ");
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
                var url = htmlPath + res.url;
                window.location.href = url;
            }
        }
    })
}

//一键返现
function passAllOrder()
{
    var rowData = $("#manageOrder_dg").datagrid('getSelections');
    console.log(rowData);
    for(var i=0;i<rowData.length;i++){
        if(rowData[i].status == "任务已提交")
        {
            agreeTask(rowData[i].user_order_id);
        }
    }
    var page = $("#manageOrder_dg").datagrid('getPager').data("pagination").options.pageNumber;
    getOrderList(page-1);
}