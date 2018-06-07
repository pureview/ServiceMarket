/**
 * Created by funing on 2018/6/1.
 */
$(function(){
    $("#manageApprentice_dg").datagrid({
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
                field: 'userID',
                title: '用户ID',
                width: '20%',
                align: 'center'
            },
            {
                field: 'masterID',
                title: '师父ID',
                width: '15%',
                align: 'center'
            },
            {
                field: 'register',
                title: '注册时间',
                width: '20%',
                align: 'center'
            },
            {
                field: 'orderNum',
                title: '订单数',
                width: '15%',
                align: 'center'
            },
            {
                field: 'taskDay',
                title: '任务间隔天数',
                width: '15%',
                align: 'center'
            },
            {
                field: 'operate',
                title: '操作',
                width: '17%',
                align: 'center',
                formatter: function(value,row,index){
                    return '<a href="#">拉黑</a> | <a href="#">升级</a>';
                }
            }]
        ]
    })
});

function onClickCell(index, field){
    if (endEditing()){
        $('#manageApprentice_dg').datagrid('selectRow', index)
            .datagrid('editCell', {index:index,field:field});
        editIndex = index;
    }
}