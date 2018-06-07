/**
 * Created by funing on 2018/6/1.
 */
/**
 * Created by funing on 2018/5/31.
 */
$(function(){
    $("#manageOrder_dg").datagrid({
        url:'datagrid_data1.json',
        fit: true,
        rownumbers : true,
        pagination : true,
        fitColumns:true,
        singleSelect:false,
        onClickCell: onClickCell,
        pageList : [ 5, 10, 15, 20 ],
        idField : 'id',
        columns:[
            [{
                field: 'taskID',
                title: '任务ID',
                width: '10%',
                align: 'center'
            },
            {
                field: 'orderID',
                title: '订单号',
                width: '10%',
                align: 'center'
            },
            {
                field: 'number',
                title: '旺旺号',
                width: '10%',
                align: 'center'
            },
            {
                field: 'userID',
                title: '用户ID',
                width: '10%',
                align: 'center'
            },
            {
                field: 'keywords',
                title: '关键词',
                width: '7%',
                align: 'center'
            },
            {
                field: 'name',
                title: '商品名',
                width: '10%',
                align: 'center'
            },
            {
                field: 'issueTime',
                title: '任务发布时间',
                width: '10%',
                align: 'center'
            },
            {
                field: 'pickTime',
                title: '接单时间',
                width: '10%',
                align: 'center'
            },
            {
                field: 'status',
                title: '状态',
                width: '5%',
                align: 'center'
            },
            {
                field: 'evaluation',
                title: '好评详情',
                width: '10%',
                align: 'center'
            },
            {
                field: 'operate',
                title: '操作',
                width: '12%',
                align: 'center',
                formatter: function(value,row,index){
                    return '<a href="#">返现</a> | <a href="#">允许提现</a>';
                }
            }]
        ],
        toolbar: [
            {
                text: '导出',
                iconCls: 'icon-save'
            }
        ]
    })
});

function onClickCell(index, field){
    if (endEditing()){
        $('#manageOrder_dg').datagrid('selectRow', index)
            .datagrid('editCell', {index:index,field:field});
        editIndex = index;
    }
}