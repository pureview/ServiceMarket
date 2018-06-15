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
        onClickCell: onClickCell,
        pageList : [ 20],
        pageSize: 20,
        idField : 'id',
        columns:[
            [{
                field: 'choose',
                align: 'center',
                checkbox: true
            },
            //[{
            //    field: 'choose',
            //    //title: '<input id="check_all" type="checkbox">',
            //    align: 'center',
            //    formatter: function(value,row,index){
            //        //console.log(row);
            //        if(row.status == "1")//0为未发布
            //            return '<input type="checkbox" disabled>';
            //        else
            //            return '<input name="check_input" type="checkbox" onclick="getRowData(\''+row+'\',\''+row.id+'\')">';
            //    }
            //},
            {
                field: 'status',
                title: '任务状态',
                align: 'center',
                formatter: function(value,row,index){
                    if(value == 0)
                        return "未发布";
                    else if(value == 1)
                        return "<span style='color:green'>已发布</span>";
                }
            },
            {
                field: 'shop',
                title: '店铺名称',
                align: 'center'
            },
            {
                field: 'keyword',
                title: '关键字',
                align: 'center'
            },
            {
                field: 'sort',
                title: '排序方式',
                align: 'center'
            },
            {
                field: 'pay_method',
                title: '付款方式',
                align: 'center'
            },
            {
                field: 'good_name',
                title: '商品全名',
                align: 'center'
            },

            {
                field: 'good_price',
                title: '价格',
                align: 'center'
            },

            {
                field: 'begin_time',
                title: '开始时间',
                align: 'center',
                formatter: function(value,row,index){
                    return change(row.begin_time);
                }
            },

            {
                field: 'end_time',
                title: '结束时间',
                align: 'center',
                formatter: function(value,row,index){
                    return change(row.end_time);
                }
            },
            {
                field: 'mission_num',
                title: '任务数量',
                align: 'center',
                formatter: function(value,row,index){
                    return "<span style='color: red'>"+row.mission_num+"</span>";
                },
                editor: {
                    type: 'validatebox',
                    options:{
                        required: true,
                        missingMessage:'请填写任务数量'
                    }
                }
            },
            {
                field: 'good_num',
                title: '商品数量',
                align: 'center',
                formatter: function(value,row,index){
                    return "<span style='color: red'>"+row.good_num+"</span>";
                },
                editor: {
                    type: 'validatebox',
                    options:{
                        required: true,
                        missingMessage:'请填写商品数量'
                    }
                }
            },
            //{
            //    field: 'master',
            //    title: '师父佣金',
            //    align: 'center',
            //    formatter: function(value,row,index){
            //            return "3";
            //    },
            //    editor: {
            //        type: 'validatebox',
            //        options: {
            //            required: true,
            //            missingMessage: '请输入师父佣金'
            //        }
            //    }
            //},
            //{
            //    field: 'apprentice',
            //    title: '徒弟佣金',
            //    align: 'center',
            //    formatter: function(value,row,index){
            //        return "<span style='color: red;'>3</span>";
            //    },
            //    editor: {
            //        type: 'validatebox',
            //        options: {
            //            required: true,
            //            missingMessage: '请输入徒弟佣金'
            //        }
            //    }
            //},
            {
                field: 'allow',
                title: '选择',
                width: '10%',
                align: 'center',
                formatter: function(value,row,index){
                    if(row.allow == "0" || row.allow == "全部")
                        return "<span style='color: red;'>全部</span>";
                    else if(row.allow == "师傅")
                        return "<span style='color: red;'>师傅</span>";
                },
                editor: {
                    type: 'combobox',
                    options: {
                        data: [{value:'全部',text:'全部'},{value:'师傅',text:'师傅'}],
                        valueFiled: 'value',
                        textFiled: 'text',
                        panelHeight: 'auto',
                        required: true,
                        missingMessage: "请选择一项"
                    }
                }
            },
            {
                field: 'operate',
                title: '操作',
                align: 'center',
                formatter: function(value,row,index){
                    if(row.status == "1")// 0为未发布
                        return '<a onclick="cancelTask(\''+row.id+'\')">取消任务</a>';
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
    if ($('#manageTask_dg').datagrid('validateRow', editIndex)){
        $('#manageTask_dg').datagrid('endEdit', editIndex);
        editIndex = undefined;
        return true;
    } else {
        return false;
    }
}
function onClickCell(index, field){
    var rows = $("#manageTask_dg").datagrid('getRows');
    var row = rows[index];
    if(row.status == 0)
    {
        if (endEditing()){
            $('#manageTask_dg').datagrid('selectRow', index)
                .datagrid('editCell', {index:index,field:field});
            editIndex = index;
        }
    }
}
//设置时间格式
function myformatter(date){
    date= new Date(Date.parse(date));
    //if(date == 'Invalid Date')
    //    return changeTime(new Date());
    //else
    //{
        var y = date.getFullYear();
        var m = date.getMonth()+1;
        var d = date.getDate();
        var h = date.getHours();
        var n = date.getMinutes();
        return y+"/"+(m<10?('0'+m):m)+"/"+(d<10?('0'+d):d)+'-'+(h<10?('0'+h):h)+":"+(n<10?('0'+n):n);
    //}
}

//checkbox全选
$("#check_all").click(function(){
    if($(this).attr('checked')=='checked'){
        $("input[name='check_input']").attr("checked",'checked');
    }else{
        $("input[name='check_input']").removeAttr("checked");
    }
});


//获取店铺列表
function getShopList()
{
    var data = {};
    data["code"] = 16;
    data["op"] = 0;
    data["seller_username"] = window.localStorage.getItem("username");
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            var data = [];
            if(res.code == "0")
            {
                for(var i=0; i<res.data.length; i++)
                {
                    var shop = {};
                    shop["id"] = res.data[i].shop;
                    shop["text"] = res.data[i].shop;
                    data.push(shop);
                }
            }
            $("#shopList").combobox("loadData", data);
        }
    })
}

//创建任务
function setupTask()
{
    var price1 = $("#price1").val();
    var price2 = $("#price2").val();
    var price = price1+"-"+price2;
    var data = new FormData();
    data.append("code","0");
    data.append("shop",$("#shopList").val());
    data.append("seller_username",window.localStorage.getItem("username"));
    data.append("images",document.getElementById("images").files[0]);
    data.append("keyword",$("#keyword").val());
    data.append("sort",$("#sort").val());
    data.append("price",price);
    data.append("pay_method",$("#pay_method").val());
    data.append("good_price",$("#good_price").val());
    data.append("good_name",$("#good_name").val());
    console.log(data);
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        dataType: 'JSON',
        processData : false,
        contentType : false,
        success: function(res){
            if(res.code == "0")
            {
                alert("创建成功");
                $("#shopList").combobox("setValue","");
                $("#images").val("");
                $("#keyword").textbox("setValue","");
                $("#sort").textbox("setValue","");
                $("#price1").textbox("setValue","");
                $("#price2").textbox("setValue","");
                $("#pay_method").textbox("setValue","");
                $("#good_price").numberbox("setValue","");
                $("#good_name").textbox("setValue","");
            }
        }
    })
}

//获取任务
function getTaskList(pageNum)
{
    if(pageNum == null)
        pageNum = 0;
    var data = {};
    data["code"] = 2;
    data["page"] = pageNum;
    data["seller_username"] = window.localStorage.getItem("username");
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

var rowData;
var mission_id;
function getRowData(row,id)
{
    rowData = row;
    mission_id = id;
    console.log(rowData);
}

//发布任务
function lanchTask()
{
    var rowData = $("#manageTask_dg").datagrid('getSelections');
    for(var i = 0; i<rowData.length;i++)
    {
        if(rowData[i].status == 0)
        {
            var mission_class = rowData[i].id;
            var begin_time;
            var end_time;
            var master_money = $("#mmaster_money").val();
            var salve_money = $("#salve_money").val();
            var good_num = rowData[i].good_num;
            var mission_num = rowData[i].mission_num;
            var allow = rowData[i].allow;
            var begin_time = changeTime($("#begin_date").val());
            var end_time = changeTime($("#end_date").val());
            var data = {};
            data["code"] = 1;
            data["mission_class"] = mission_class;//任务id
            data["begin_time"] = begin_time;
            data["end_time"] = end_time;
            data["master_money"] = master_money;
            data["slave_money"] = salve_money;
            data["allow"] = allow; //0全部 1师父
            data["good_num"] = good_num;
            data["mission_num"] = mission_num;
            data["seller_username"] = window.localStorage.getItem("username");
            console.log(data);
            $.ajax({
                url: url,
                type: 'post',
                data: data,
                success: function(res)
                {
                    res = JSON.parse(res);
                    if(res.code == "0")
                    {
                        //alert("发布成功");
                        $("#manageTask_dg").html("");
                        var page = $("#manageTask_dg").datagrid('getPager').data("pagination").options.pageNumber;
                        getTaskList(page-1);
                    }
                    else
                    {
                        alert("发布失败");
                        var page = $("#manageTask_dg").datagrid('getPager').data("pagination").options.pageNumber;
                        getTaskList(page-1);
                    }
                }
            });
        }
    }
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

function getThisValue(index)
{
    var editors = $('#manageTask_dg').datagrid('getEditors', index);
    console.info(editors[8]);
}