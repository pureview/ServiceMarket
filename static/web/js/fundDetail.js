/**
 * Created by funing on 2018/5/31.
 */
$(function(){
    var dg = $("#fundDetail_dg").datagrid({
        fit: true,
        rownumbers : true,
        pagination : false,
        fitColumns:true,
        singleSelect:false,
        onClickCell: onClickCell,
        pageList : [ 5, 10, 15, 20 ],
        idField : 'id',
        columns:[
            [{
                field: 'mission_money',
                title: '佣金花费',
                width: '20%',
                align: 'center'
            },
            {
                field: 'good_price',
                title: '本金花费',
                width: '20%',
                align: 'center'
            },
            {
                field: 'master_money',
                title: '师父佣金',
                width: '20%',
                align: 'center'
            },
            {
                field: 'slave_money',
                title: '徒弟佣金',
                width: '20%',
                align: 'center'
            }]
        ],
        toolbar: "#searchtool"
    });
});

function onClickCell(index, field){
    if (endEditing()){
        $('#fundDetail_dg').datagrid('selectRow', index)
            .datagrid('editCell', {index:index,field:field});
        editIndex = index;
    }
}

//获取资金明细
function  getFundDetail(pageNum)
{
    if(pageNum == null)
        pageNum = 0;
    var data = {};
    var begin = $("#begin_date").val();
    var end = $("#end_date").val();
    data["code"] = 11;
    data["page"] = pageNum;
    data["seller_username"] = window.localStorage.getItem("username");
    data["begin_date"] = begin;
    data["end_date"] = end;
    console.log(data);
    if(begin == undefined || end == undefined)
    {
        alert("请填写起止时间");
    }
    else{
        $.ajax({
            url: url,
            type: 'post',
            data: data,
            success: function(res){
                res = JSON.parse(res);
                console.log(res);
                if(res.code == "0")
                {
                    $("#good_price").text(res.good_price);
                    $("#mission_money").text(res.mission_money);
                    $("#order_num").text(res.order_num);
                    var row = [];
                    for(var i=0; i<res.data.length;i++)
                    {
                        row.push(res.data[i]);
                    }
                    $("#fundDetail_dg").datagrid('loadData',{ total: res.data.length, rows: row });
                }
            }
        })
    }
}
