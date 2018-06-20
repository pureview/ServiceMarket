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
        //onClickCell: onClickCell,
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
                title: '用户名',
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
                align: 'center'
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
                field: 'status',
                title: '状态',
                align: 'center'
            },
            {
                field: 'master_money',
                title: '师父佣金',
                align: 'center'
            },
            {
                field: 'slave_money',
                title: '徒弟佣金',
                align: 'center'
            },
            {
                field: 'operate',
                title: '操作',
                align: 'center',
                formatter: function(value,row,index){
                    if(row.status == "任务已提交")
                        return '<button onclick="agreeTask(\''+row.user_order_id+'\')">返现</button> | <button onclick="disagreeTask(\''+row.user_order_id+'\')">拒绝</button>';
                }
            }]
        ],
        toolbar: "#searchtool"
    });
    mdg.datagrid('getPager').pagination({
        displayMsg:'当前显示第 {from}-{to} 条记录 ， 共 {total} 条记录',
        onSelectPage:function(pageNumber){
            getOrderList(pageNumber-1);
        }
    });
});

//获取订单列表
function getOrderList(pageNum)
{
    var begin_time = $("#begin_date").val();
    var end_time = $("#end_date").val();
    var status = $("#status").val();
    var shop =$("#shop").val();
    var good_name = $("#good_name").val();
    if(pageNum == null)
        pageNum = 0;
    var data = {};
    data["code"] = "10";
    data["seller_username"] = window.localStorage.getItem("username");
    data["page"] = pageNum;
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
            }
        }
    })
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

//导出excel
function dataExcel()
{
    var rowData = $("#manageOrder_dg").datagrid('getSelections');
    var id_arr = [];
    console.log(rowData);
    for(var i=0;i<rowData.length;i++)
    {
        id_arr.push(rowData[i].mission_id);
    }
    //var begin_time = getTodayTime($("#begin_date").val());
    //var end_time = getNextTime($("#end_date").val());
    //console.log(begin_time);
    //console.log(end_time);
    var data = {};
    data["code"] = "38";
    data["seller_username"] = window.localStorage.getItem("username");
    data["mission_ids"] = id_arr.join(" ");
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